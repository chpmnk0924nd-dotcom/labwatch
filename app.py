from flask import Flask, render_template
import yaml
import socket
import requests
from datetime import datetime
from urllib.parse import urlparse

app = Flask(__name__)


def load_services():
    with open("services.yml", "r") as file:
        data = yaml.safe_load(file)
    return data.get("services", [])


def check_dns(hostname):
    try:
        ip_address = socket.gethostbyname(hostname)
        return {
            "dns_status": "OK",
            "ip_address": ip_address
        }
    except socket.gaierror:
        return {
            "dns_status": "FAILED",
            "ip_address": "Not resolved"
        }


def check_port(hostname, port):
    try:
        with socket.create_connection((hostname, port), timeout=3):
            return "OPEN"
    except OSError:
        return "CLOSED"


def check_http(url):
    try:
        response = requests.get(url, timeout=5, verify=False)
        return {
            "http_status": response.status_code,
            "reachable": True
        }
    except requests.exceptions.RequestException:
        return {
            "http_status": "No response",
            "reachable": False
        }


def check_service(service):
    name = service.get("name")
    url = service.get("url")
    host = service.get("host")
    port = service.get("port")
    category = service.get("category", "Uncategorized")

    dns_result = check_dns(host)
    port_result = check_port(host, port)

    parsed_url = urlparse(url)
    if parsed_url.scheme in ["http", "https"]:
        http_result = check_http(url)
    else:
        http_result = {
            "http_status": "Not checked",
            "reachable": False
        }

    if dns_result["dns_status"] == "OK" and port_result == "OPEN" and http_result["http_status"] == 200:
        overall_status = "Online"
        status_note = "DNS resolved, port is open, and HTTP returned 200."

    elif dns_result["dns_status"] == "OK" and port_result == "OPEN":
        overall_status = "Online"
        status_note = "DNS resolved and port is open. HTTP did not return 200, but the service appears reachable."

    elif dns_result["dns_status"] == "OK" and port_result == "CLOSED":
        overall_status = "Warning"
        status_note = "DNS resolved, but the service port is closed. Check the service, firewall, or port number."

    else:
        overall_status = "Offline"
        status_note = "Hostname did not resolve. Check Windows Server DNS or the service hostname."

    return {
        "name": name,
        "url": url,
        "host": host,
        "port": port,
        "category": category,
        "dns_status": dns_result["dns_status"],
        "ip_address": dns_result["ip_address"],
        "port_status": port_result,
        "http_status": http_result["http_status"],
        "overall_status": overall_status,
        "status_note": status_note
    }


@app.route("/")
def dashboard():
    services = load_services()
    checked_services = [check_service(service) for service in services]

    total_services = len(checked_services)
    online_count = sum(1 for service in checked_services if service["overall_status"] == "Online")
    warning_count = sum(1 for service in checked_services if service["overall_status"] == "Warning")
    offline_count = sum(1 for service in checked_services if service["overall_status"] == "Offline")
    if total_services > 0:
       health_percent = round((online_count / total_services) * 100)
    else:
       health_percent = 0

    if health_percent >= 90:
       health_status = "good"
    elif health_percent >= 70:
       health_status = "warning"
    else:
       health_status = "critical"

    return render_template(
        "index.html",
        services=checked_services,
        total_services=total_services,
        online_count=online_count,
        warning_count=warning_count,
        offline_count=offline_count,
        health_percent=health_percent,
        health_status=health_status,
        last_checked=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()
    app.run(host="0.0.0.0", port=5050, debug=True)