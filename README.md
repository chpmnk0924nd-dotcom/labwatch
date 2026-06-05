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

