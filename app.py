from security_watch import get_latest_security_report
from backup_watch import get_backup_status
from flask import Flask, render_template, send_from_directory, request, redirect
from db import (
    save_service_check,
    get_recent_service_checks,
    get_last_service_status,
    save_incident,
    get_recent_incidents,
    create_maintenance_window,
    get_active_maintenance_windows,
    get_active_maintenance_for_service,
    end_maintenance_window,
    get_service_uptime,
    get_reliability_summary,
    get_asset_inventory,
)
import yaml
import socket
import requests
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

app = Flask(__name__)
FAVICON_DIR = Path(app.root_path) / "favicon_io"


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

    checked_service = {
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
        "status_note": status_note,
    }

    maintenance = get_active_maintenance_for_service(name)

    if maintenance is not None:
        checked_service["overall_status"] = "Maintenance"
        checked_service["status"] = "Maintenance"
        checked_service["status_note"] = f"Maintenance: {maintenance[2]}"
        checked_service["maintenance_reason"] = maintenance[2]

        save_service_check(checked_service)
        return checked_service

    last_status = get_last_service_status(name)
    current_status = checked_service["overall_status"]

    # print(f"[INCIDENT DEBUG] {name}: last={last_status}, current={current_status}")

    if last_status is not None and last_status != current_status:
        save_incident(checked_service, last_status, current_status)

    save_service_check(checked_service)

    return checked_service


@app.route("/")
def dashboard():
    services = load_services()
    checked_services = []

    for service in services:
        checked_service = check_service(service)
        checked_service["uptime_24h"] = get_service_uptime(checked_service["name"], 24)
        checked_services.append(checked_service)

    total_services = len(checked_services)
    online_count = sum(1 for service in checked_services if service["overall_status"] == "Online")
    warning_count = sum(1 for service in checked_services if service["overall_status"] == "Warning")
    offline_count = sum(1 for service in checked_services if service["overall_status"] == "Offline")
    maintenance_count = sum(1 for service in checked_services if service["overall_status"] == "Maintenance")
    active_services = total_services - maintenance_count

    if active_services > 0:
        health_percent = round((online_count / active_services) * 100)
    else:
        health_percent = 100

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
        maintenance_count=maintenance_count,
        last_checked=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


@app.route("/history")
def history():
    service_history = get_recent_service_checks(50)
    return render_template("history.html", service_history=service_history)


@app.route("/incidents")
def incidents():
    incident_history = get_recent_incidents(50)
    return render_template("incidents.html", incident_history=incident_history)


@app.route("/security")
def security():
    report = get_latest_security_report()
    return render_template("security.html", report=report)


@app.route("/favicon_io/<path:filename>")
def favicon(filename):
    return send_from_directory(FAVICON_DIR, filename)


@app.route("/health")
def health():
    return "OK", 200


@app.route("/maintenance")
def maintenance():
    active_maintenance = get_active_maintenance_windows()

    service_names = []
    try:
        with open("services.yml", "r") as file:
            data = yaml.safe_load(file) or {}

            if isinstance(data, dict):
                services = data.get("services", [])
            elif isinstance(data, list):
                services = data
            else:
                services = []

            service_names = [
                service.get("name")
                for service in services
                if isinstance(service, dict) and service.get("name")
            ]
    except Exception as e:
        print(f"Error loading services.yml for maintenance page: {e}")
        service_names = []

    return render_template(
        "maintenance.html",
        active_maintenance=active_maintenance,
        service_names=service_names,
    )


@app.route("/maintenance/add", methods=["POST"])
def add_maintenance():
    service_name = request.form.get("service_name")
    reason = request.form.get("reason")

    if service_name and reason:
        create_maintenance_window(service_name, reason)

    return redirect("/maintenance")


@app.route("/maintenance/end/<int:maintenance_id>", methods=["POST"])
def end_maintenance(maintenance_id):
    end_maintenance_window(maintenance_id)
    return redirect("/maintenance")


@app.route("/reliability")
def reliability():
    reliability_24h = get_reliability_summary(24)
    reliability_7d = get_reliability_summary(168)

    return render_template(
        "reliability.html",
        reliability_24h=reliability_24h,
        reliability_7d=reliability_7d,
    )


@app.route("/backups")
def backups():
    backup_status = get_backup_status()
    return render_template("backups.html", backup_status=backup_status)


@app.route("/assets")
def assets():
    asset_inventory = get_asset_inventory()

    total_assets = len(asset_inventory)

    current_count = sum(
        1 for asset in asset_inventory
        if asset[11] == "Current"
    )

    updates_count = sum(
        1 for asset in asset_inventory
        if asset[11] == "Updates Available"
    )

    security_updates_count = sum(
        1 for asset in asset_inventory
        if asset[11] == "Security Updates Required"
    )

    return render_template(
        "assets.html",
        asset_inventory=asset_inventory,
        total_assets=total_assets,
        current_count=current_count,
        updates_count=updates_count,
        security_updates_count=security_updates_count,
    )


if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()
    app.run(host="0.0.0.0", port=5050, debug=False)