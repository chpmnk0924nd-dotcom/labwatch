#!/usr/bin/env python3

import os

import re

import glob

import gzip

import shutil

import socket

import subprocess

from collections import Counter

from datetime import datetime

from pathlib import Path



REPORT_DIR = Path("reports")

LATEST_REPORT = REPORT_DIR / "latest_security_report.txt"


AUTH_LOG_PATHS = [

    "/var/log/auth.log",

    "/var/log/auth.log.1",

]


NPM_LOG_PATHS = [

    "/opt/npm/data/logs/*access.log*",

    "/data/logs/*access.log*",

    "/home/*/npm/data/logs/*access.log*",

    "/home/*/nginx-proxy-manager/data/logs/*access.log*",

    "/var/lib/docker/volumes/npm_data/_data/logs/*access.log*",

]


RISKY_PORTS = {

    21: "FTP",

    22: "SSH",

    23: "Telnet",

    25: "SMTP",

    53: "DNS",

    80: "HTTP",

    110: "POP3",

    139: "NetBIOS",

    143: "IMAP",

    389: "LDAP",

    443: "HTTPS",

    445: "SMB",

    3306: "MySQL",

    3389: "RDP",

    5432: "PostgreSQL",

    6379: "Redis",

    8080: "HTTP Alt",

    8443: "HTTPS Alt",

    9200: "Elasticsearch",

}



def run_command(command):

    try:

        result = subprocess.run(

            command,

            shell=True,

            text=True,

            capture_output=True,

            timeout=15,

        )

        return result.stdout.strip(), result.stderr.strip(), result.returncode

    except subprocess.TimeoutExpired:

        return "", "Command timed out", 1

    except Exception as exc:

        return "", str(exc), 1



def read_text_file(path):

    try:

        if path.endswith(".gz"):

            with gzip.open(path, "rt", errors="ignore") as file:

                return file.read()

        with open(path, "r", errors="ignore") as file:

            return file.read()

    except Exception:

        return ""



def write_section(file, title):

    file.write("\n")

    file.write("=" * 80 + "\n")

    file.write(f"{title}\n")

    file.write("=" * 80 + "\n")



def get_hostname():

    try:

        return socket.gethostname()

    except Exception:

        return "unknown-host"



def get_ip_addresses():

    stdout, stderr, code = run_command("hostname -I")

    if stdout:

        return stdout.strip()

    return "Unable to determine IP address"



def check_ssh_logs(file):

    write_section(file, "SSH Login Activity")


    found_logs = []

    for path in AUTH_LOG_PATHS:

        if os.path.exists(path):

            found_logs.append(path)


    if not found_logs:

        stdout, stderr, code = run_command("journalctl -u ssh --no-pager -n 200")

        if stdout:

            auth_text = stdout

            file.write("Source: journalctl -u ssh\n\n")

        else:

            file.write("No SSH auth logs found from /var/log/auth.log or journalctl.\n")

            return

    else:

        auth_text = ""

        for path in found_logs:

            auth_text += read_text_file(path)

        file.write(f"Sources: {', '.join(found_logs)}\n\n")


    failed = re.findall(r"Failed password.*from ([0-9.]+)", auth_text)

    accepted = re.findall(r"Accepted .* for .* from ([0-9.]+)", auth_text)

    invalid = re.findall(r"Invalid user .* from ([0-9.]+)", auth_text)


    file.write(f"Failed SSH attempts: {len(failed)}\n")

    file.write(f"Successful SSH logins: {len(accepted)}\n")

    file.write(f"Invalid user attempts: {len(invalid)}\n\n")


    if failed:

        file.write("Top failed SSH source IPs:\n")

        for ip, count in Counter(failed).most_common(10):

            file.write(f"  {ip}: {count}\n")

    else:

        file.write("No failed SSH attempts found.\n")


    file.write("\n")


    if accepted:

        file.write("Successful SSH login source IPs:\n")

        for ip, count in Counter(accepted).most_common(10):

            file.write(f"  {ip}: {count}\n")

    else:

        file.write("No successful SSH logins found in parsed logs.\n")



def check_crowdsec(file):

    write_section(file, "CrowdSec Alerts and Decisions")


    stdout, stderr, code = run_command("which cscli")

    if code != 0 or not stdout:

        file.write("CrowdSec cscli not found on this system.\n")

        return


    alerts, alerts_err, alerts_code = run_command("sudo cscli alerts list -o human")

    decisions, decisions_err, decisions_code = run_command("sudo cscli decisions list -o human")


    file.write("CrowdSec Alerts:\n")

    if alerts:

        file.write(alerts + "\n")

    else:

        file.write("No CrowdSec alerts returned.\n")

        if alerts_err:

            file.write(f"Error: {alerts_err}\n")


    file.write("\nCrowdSec Decisions:\n")

    if decisions:

        file.write(decisions + "\n")

    else:

        file.write("No active CrowdSec decisions returned.\n")

        if decisions_err:

            file.write(f"Error: {decisions_err}\n")



def find_npm_logs():

    found = []

    for pattern in NPM_LOG_PATHS:

        found.extend(glob.glob(pattern))


    unique = sorted(set(found))

    return unique



def check_npm_logs(file):

    write_section(file, "Nginx Proxy Manager Web Probes")


    logs = find_npm_logs()


    if not logs:

        file.write("No Nginx Proxy Manager access logs found.\n")

        file.write("\nChecked paths:\n")

        for path in NPM_LOG_PATHS:

            file.write(f"  {path}\n")

        return


    file.write(f"Nginx Proxy Manager access logs found: {len(logs)}\n")

    file.write("Showing newest matched files first.\n\n")


    logs = sorted(logs, key=lambda p: os.path.getmtime(p), reverse=True)


    combined_text = ""

    for log_path in logs[:20]:

        file.write(f"Log: {log_path}\n")

        text = read_text_file(log_path)

        combined_text += text[-50000:] + "\n"


    if not combined_text.strip():

        file.write("\nLogs were found, but Security Watch could not read their contents.\n")

        file.write("This is probably a permissions issue.\n")

        return


    ips = re.findall(r"\b(?:client: )?([0-9]{1,3}(?:\.[0-9]{1,3}){3})\b", combined_text)

    status_codes = re.findall(r'\s([1-5][0-9]{2})\s', combined_text)

    suspicious_paths = re.findall(

        r'"(?:GET|POST|HEAD) ([^"]*(?:wp-admin|wp-login|\.env|phpmyadmin|admin|login|shell|cgi-bin|xmlrpc)[^"]*)',

        combined_text,

        re.IGNORECASE,

    )


    file.write("\nTop source IPs seen in NPM access logs:\n")

    if ips:

        for ip, count in Counter(ips).most_common(10):

            file.write(f"  {ip}: {count}\n")

    else:

        file.write("  No source IPs parsed.\n")


    file.write("\nHTTP status code summary:\n")

    if status_codes:

        for code, count in Counter(status_codes).most_common():

            file.write(f"  {code}: {count}\n")

    else:

        file.write("  No HTTP status codes parsed.\n")


    file.write("\nSuspicious web probe paths:\n")

    if suspicious_paths:

        for path, count in Counter(suspicious_paths).most_common(15):

            file.write(f"  {path}: {count}\n")

    else:

        file.write("  No obvious suspicious web probe paths found.\n")



def check_listening_ports(file):

    write_section(file, "Listening Ports")


    stdout, stderr, code = run_command("ss -tulpen")

    if not stdout:

        stdout, stderr, code = run_command("ss -tulpn")


    if not stdout:

        file.write("Could not collect listening ports with ss.\n")

        if stderr:

            file.write(f"Error: {stderr}\n")

        return


    file.write(stdout + "\n")



def check_risky_ports(file):

    write_section(file, "Risky Port Summary")


    stdout, stderr, code = run_command("ss -tuln")

    if not stdout:

        file.write("Could not collect port summary.\n")

        return


    found_ports = []


    for line in stdout.splitlines():

        matches = re.findall(r":([0-9]+)\s", line)

        for match in matches:

            port = int(match)

            if port in RISKY_PORTS:

                found_ports.append(port)


    if not found_ports:

        file.write("No commonly risky ports found listening.\n")

        return


    for port in sorted(set(found_ports)):

        file.write(f"Port {port}: {RISKY_PORTS[port]} is listening\n")



def check_system_summary(file):

    write_section(file, "System Summary")


    file.write(f"Hostname: {get_hostname()}\n")

    file.write(f"IP Addresses: {get_ip_addresses()}\n")

    file.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")


    uptime, _, _ = run_command("uptime")

    if uptime:

        file.write(f"Uptime: {uptime}\n")


    disk, _, _ = run_command("df -h /")

    if disk:

        file.write("\nDisk usage:\n")

        file.write(disk + "\n")


    memory, _, _ = run_command("free -h")

    if memory:

        file.write("\nMemory usage:\n")

        file.write(memory + "\n")



def generate_report():

    REPORT_DIR.mkdir(exist_ok=True)


    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    report_path = REPORT_DIR / f"security-watch-{timestamp}.txt"


    with open(report_path, "w") as file:

        file.write("SECURITY WATCH REPORT\n")

        file.write("=" * 80 + "\n")

        file.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        file.write(f"Host: {get_hostname()}\n")

        file.write(f"IPs: {get_ip_addresses()}\n")


        check_system_summary(file)

        check_ssh_logs(file)

        check_crowdsec(file)

        check_npm_logs(file)

        check_risky_ports(file)

        check_listening_ports(file)


        write_section(file, "Summary")

        file.write("Security Watch completed successfully.\n")

        file.write("Review SSH activity, CrowdSec alerts, Nginx Proxy Manager probes, and listening ports.\n")


    shutil.copyfile(report_path, LATEST_REPORT)


    print(f"Report generated: {report_path}")

    print(f"Latest report updated: {LATEST_REPORT}")



if __name__ == "__main__":

    generate_report()
