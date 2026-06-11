\# LabWatch



LabWatch is a custom Flask-based dashboard built to monitor my homelab infrastructure.



It checks core services in my environment and displays their status in a clean web dashboard. The goal of this project is to demonstrate practical IT skills in monitoring, DNS validation, TCP port checks, HTTP health checks, troubleshooting, and infrastructure documentation.



\## Features



\- Web dashboard built with Python Flask

\- YAML-based service configuration

\- DNS resolution checks

\- TCP port availability checks

\- HTTP status checks

\- Diagnostic status notes

\- Color-coded service cards

\- Screenshots for documentation and portfolio use



\## Services Monitored



LabWatch currently monitors:



\- Grafana

\- Prometheus

\- Alertmanager

\- kube-state-metrics

\- Nginx Proxy Manager

\- Keycloak

\- Wazuh

\- Proxmox

\- OPNsense



\## Technologies Used



\- Python

\- Flask

\- PyYAML

\- Requests

\- HTML

\- CSS

\- Git / GitHub



\## Project Structure



```text

labwatch/

├── app.py

├── services.yml

├── requirements.txt

├── templates/

│   └── index.html

├── static/

│   └── style.css

├── screenshots/

│   ├── labwatch-v1-all-online.png

│   └── labwatch-v2-nine-services-online.png

└── .gitignore

## PostgreSQL Service History

LabWatch now stores service check history in a PostgreSQL database hosted on a FreeBSD VM. Each service check records the service name, status, host, port, category, URL, diagnostic note, and timestamp.

### Components

- LabWatch Flask app running on Windows
- PostgreSQL 16 running on FreeBSD
- FreeBSD VM IP: 192.168.10.100
- Database: labwatch
- Table: service_checks
- History page: /history

### Features

- Live service dashboard
- PostgreSQL-backed historical service checks
- Dedicated `/history` page
- Service categories and diagnostic notes
- FreeBSD Web and PostgreSQL monitoring

## LabWatch Homelab Command Center

LabWatch is a Flask-based homelab monitoring dashboard that tracks service availability, incident history, service health, and security reports across my home lab environment.

Current capabilities:
- Monitors 21 services across Windows, Linux, FreeBSD, Proxmox, OPNsense, Kubernetes, storage, and network devices
- Tracks service history in PostgreSQL
- Records incidents when services change status
- Displays automated Security Watch reports
- Parses Nginx Proxy Manager access logs for source IPs, status codes, and web probe activity
- Pulls security reports automatically from Ubuntu using SSH key authentication
- Recovers after restart using scheduled tasks, cron, and service auto-start settings

## Recovery Scenario: Hyper-V External Switch Failure

After a restart, LabWatch showed degraded service health. DC01 could reach the gateway and other LAN devices, but the Windows host and DC01 could not communicate with each other. The issue was traced to a broken Hyper-V External Switch binding.

Resolution:
- Rebuilt the Hyper-V LAB-SWITCH external virtual switch
- Reattached DC01 to the recreated switch
- Confirmed host-to-VM communication
- Verified Windows Server DNS and LDAP checks returned online
- Restored LabWatch to 21/21 services online