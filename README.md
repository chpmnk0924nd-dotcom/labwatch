# LabWatch — Homelab Monitoring, Security, and Reliability Dashboard

LabWatch is a Flask-based homelab command center that monitors service availability, records service history, tracks incidents, displays automated security reports, and calculates reliability metrics across my home lab environment.

This project was built as a hands-on IT infrastructure portfolio project to practice systems administration, monitoring, networking, security visibility, automation, database integration, and troubleshooting.

---

## Project Summary

LabWatch provides a centralized dashboard for monitoring my homelab services across Windows, Linux, FreeBSD, Docker, Proxmox, Kubernetes, network devices, storage, and security tools.

The dashboard currently monitors **21 services** and includes:

* Live service health checks
* DNS, port, and HTTP validation
* PostgreSQL-backed service history
* Incident tracking for status changes
* Maintenance Mode for planned service work
* Reliability and uptime reporting
* Automated Security Watch report viewing
* Nginx Proxy Manager access log parsing
* Hourly report generation and automated report pulling
* Startup automation using Windows Scheduled Tasks and Linux cron

---

## Current Status

LabWatch is currently operational with:

* **21 total monitored services**
* **21 services online**
* **0 warnings**
* **0 offline**
* **100% overall dashboard health**

The project includes monitoring, incident tracking, maintenance workflows, reliability metrics, and automated security reporting.

---

## Screenshots

> Screenshots are stored in the `screenshots/` folder.

Recommended screenshots to include in the repository:

```text
screenshots/labwatch-dashboard-21-online.png
screenshots/labwatch-history-page.png
screenshots/labwatch-incidents-page.png
screenshots/labwatch-security-watch-npm-logs.png
screenshots/labwatch-maintenance-mode.png
screenshots/labwatch-reliability-page.png
```

Example README image links:

```markdown
![LabWatch Dashboard](screenshots/labwatch-dashboard-21-online.png)
![Security Watch Report](screenshots/labwatch-security-watch-npm-logs.png)
![Reliability Metrics](screenshots/labwatch-reliability-page.png)
```

---

## Features

### Live Service Monitoring

LabWatch checks each configured service and displays:

* Service name
* Category
* Hostname
* Resolved IP address
* Port status
* DNS status
* HTTP status
* Overall service status
* Status notes
* 24-hour uptime percentage

Each service card is color-coded based on status.

Supported statuses include:

```text
Online
Warning
Offline
Maintenance
```

---

### PostgreSQL Service History

Every service check is written to a PostgreSQL database running on a FreeBSD server.

The history page allows me to review recent service checks and see how services behaved over time.

Database-backed history makes LabWatch more than a static dashboard. It stores real operational data that can be used for uptime metrics, troubleshooting, and incident analysis.

---

### Incident Tracking

LabWatch records incidents when a service changes state.

Example:

```text
Online -> Warning
Warning -> Online
Online -> Offline
Offline -> Online
```

The incident timeline helps show when problems started and when they recovered.

This was tested by intentionally changing a service port and confirming LabWatch recorded the status transition.

---

### Maintenance Mode

Maintenance Mode allows planned service work without treating the service as a normal outage.

A service can be marked as under maintenance with a reason such as:

```text
Testing maintenance mode
Updating Wazuh dashboard
Restarting Nginx Proxy Manager
Patching Windows Server
```

When a service is in maintenance:

* The dashboard shows the service as Maintenance
* The maintenance reason appears in the status note
* The service is excluded from downtime calculations
* Normal incident generation is skipped for that service

This adds a real-world monitoring workflow similar to what production monitoring tools provide.

---

### Reliability Metrics and Uptime Reporting

LabWatch calculates service uptime from PostgreSQL service check history.

Each service card now displays:

```text
Uptime 24h: 100.0%
```

A dedicated Reliability page shows:

* 24-hour uptime
* 7-day uptime
* Total checks
* Online checks
* Problem checks
* Maintenance checks

Maintenance windows are excluded from downtime calculations so planned work does not unfairly reduce uptime.

---

### Security Watch Integration

Security Watch is a companion script that runs on an Ubuntu server and generates automated security reports.

Security Watch collects and summarizes:

* System summary
* SSH login activity
* Failed SSH attempts
* Successful SSH logins
* CrowdSec alerts
* CrowdSec decisions
* Nginx Proxy Manager web probe activity
* Risky listening ports
* Full listening port details

The latest report is pulled automatically into LabWatch and displayed at:

```text
/security
```

---

### Nginx Proxy Manager Log Parsing

Security Watch parses Nginx Proxy Manager access logs directly from Docker volume storage.

The log path used is:

```text
/var/lib/docker/volumes/npm_data/_data/logs/*access.log*
```

The report summarizes:

* Nginx Proxy Manager access logs found
* Top source IPs
* HTTP status code counts
* Suspicious web probe paths

Example status code summary:

```text
200
301
302
401
403
404
499
```

This provides visibility into reverse proxy traffic and web probing activity.

---

### Automation

LabWatch and Security Watch use automation on both Windows and Linux.

#### Ubuntu Security Watch Automation

Security Watch runs hourly using cron:

```cron
0 * * * * /home/nick/Projects/homelab-security-watch/run-security-watch-latest.sh >> /home/nick/Projects/homelab-security-watch/security-watch-cron.log 2>&1
```

The script generates a new report and updates:

```text
reports/latest_security_report.txt
```

#### Windows Report Pull Automation

The Windows LabWatch host pulls the latest Security Watch report using an SSH key and a scheduled task.

The report is copied into:

```text
D:\Scripts\LabWatch\security_reports\latest_security_report.txt
```

#### LabWatch Startup Automation

LabWatch can be started automatically after a Windows restart using a scheduled task and:

```text
start_labwatch.ps1
```

Scheduled task exports are documented in the `docs/` folder.

---

## Monitored Services

LabWatch currently monitors 21 services across the homelab.

### Monitoring

* Grafana
* Prometheus
* Alertmanager
* LabWatch Dashboard
* LabWatch History Page
* LabWatch Incidents Page
* LabWatch Flask Health

### Kubernetes

* kube-state-metrics

### Reverse Proxy

* Nginx Proxy Manager

### Identity and Security

* Keycloak
* Wazuh
* Security Watch
* CrowdSec visibility through Security Watch reports

### Virtualization

* Proxmox

### Firewall and Network

* OPNsense
* Switch Management

### FreeBSD and Database

* FreeBSD Web
* FreeBSD PostgreSQL

### Windows Infrastructure

* Windows Server DNS
* Windows Server LDAP

### Linux Systems

* Ubuntu Security Watch Host
* Ubuntu Desktop

### Storage

* NAS

---

## Architecture

LabWatch uses multiple systems working together:

```text
Windows Host
    Runs LabWatch Flask dashboard
    Pulls Security Watch reports
    Runs scheduled tasks

FreeBSD Server
    Runs PostgreSQL database
    Stores service history
    Stores incidents
    Stores maintenance windows

Ubuntu Server
    Runs Security Watch
    Generates hourly reports
    Parses NPM logs
    Collects security information

Windows Server DC01
    Provides DNS
    Provides LDAP / Active Directory services

Proxmox
    Virtualization platform

OPNsense
    Firewall and router

Nginx Proxy Manager
    Reverse proxy
    Access log source

NAS
    Storage and backup target
```

---

## Data Flow

```text
1. LabWatch loads services from services.yml.
2. LabWatch checks DNS, ports, and HTTP status.
3. Service checks are saved to PostgreSQL.
4. Status changes are saved as incidents.
5. Maintenance windows are checked before incident creation.
6. Reliability metrics are calculated from service history.
7. Security Watch runs hourly on Ubuntu.
8. Windows pulls the latest Security Watch report.
9. LabWatch displays the report on the Security Watch page.
```

---

## Pages Built

LabWatch currently includes the following pages:

```text
/              Dashboard
/history       Service history
/incidents     Incident timeline
/security      Security Watch report
/maintenance   Maintenance Mode
/reliability   Reliability metrics and uptime reporting
/health        Lightweight Flask health check
```

---

## Technology Stack

### Backend

* Python
* Flask
* PostgreSQL
* psycopg2
* PyYAML
* Requests

### Frontend

* HTML
* CSS
* Jinja templates

### Infrastructure

* Windows 10/11 Host
* Windows Server DC01
* Ubuntu Server
* FreeBSD Server
* Proxmox VE
* OPNsense
* Docker
* Nginx Proxy Manager
* k3s Kubernetes
* NAS storage

### Monitoring and Security

* Prometheus
* Grafana
* Alertmanager
* Loki
* Wazuh
* CrowdSec
* Security Watch custom script
* Nginx Proxy Manager access logs

### Automation

* Windows Scheduled Tasks
* Linux cron
* SSH key authentication
* SCP report transfer

---

## Database Tables

LabWatch uses PostgreSQL tables for persistent data.

### service_checks

Stores each service check.

```text
id
service_name
status
checked_at
host
port
category
url
status_note
```

### incidents

Stores service status transitions.

```text
id
service_name
old_status
new_status
host
port
category
note
created_at
```

### maintenance_windows

Stores active and historical maintenance windows.

```text
id
service_name
reason
start_time
end_time
active
created_at
```

---

## Configuration

Services are configured in:

```text
services.yml
```

Example service entry:

```yaml
- name: Grafana
  url: http://grafana.homelab.local
  host: grafana.homelab.local
  port: 80
  category: Monitoring
```

Sensitive configuration is stored in:

```text
.env
```

The `.env` file is intentionally ignored by Git.

---

## Security Notes

The following files and folders should not be committed:

```text
.env
security_reports/
reports/
security-watch-cron.log
SSH private keys
database passwords
generated reports with sensitive data
```

The repository includes source code, documentation, scripts, and screenshots, but avoids committing secrets and generated security reports.

---

## Recovery Scenario: Hyper-V External Switch Failure

A major troubleshooting milestone occurred after a restart when several LabWatch cards reported warnings or offline status.

Symptoms included:

```text
Windows Server DNS warning
Windows Server LDAP warning
Nginx Proxy Manager offline
Wazuh offline
Host could not reach DC01
DC01 could reach other LAN systems but not the Windows host
```

Troubleshooting showed that the Hyper-V external virtual switch binding was broken.

The fix was:

```text
1. Shut down DC01.
2. Remove the broken LAB-SWITCH Hyper-V external switch.
3. Recreate LAB-SWITCH as an External switch.
4. Bind it to the Realtek 5GbE adapter.
5. Enable "Allow management operating system to share this network adapter."
6. Reattach DC01 to the recreated switch.
7. Restart DC01.
8. Verify host-to-VM communication.
9. Refresh LabWatch.
```

Result:

```text
21/21 services online
0 warnings
0 offline
100% health
```

This became an important troubleshooting and recovery documentation milestone.

---

## Skills Demonstrated

This project demonstrates practical hands-on experience with:

* Python application development
* Flask web dashboards
* PostgreSQL database integration
* Linux administration
* FreeBSD administration
* Windows Server administration
* DNS troubleshooting
* LDAP / Active Directory service checks
* Hyper-V troubleshooting
* Proxmox virtualization
* Docker container log discovery
* Nginx Proxy Manager log parsing
* SSH key authentication
* SCP automation
* Windows Scheduled Tasks
* Linux cron jobs
* Incident tracking
* Maintenance workflows
* Uptime and reliability calculations
* Security reporting
* Network troubleshooting
* Git and GitHub documentation

---

## Project Milestones

### Milestone 1 — Basic Dashboard

Built the first Flask dashboard to monitor core homelab services.

### Milestone 2 — Expanded Service Checks

Added DNS, port, and HTTP validation across the lab.

### Milestone 3 — PostgreSQL History

Integrated FreeBSD PostgreSQL to store service check history.

### Milestone 4 — Incident Tracking

Added incident detection for service status changes.

### Milestone 5 — Security Watch Integration

Displayed automated security reports inside LabWatch.

### Milestone 6 — NPM Log Parsing

Added Nginx Proxy Manager access log parsing for source IP and HTTP status summaries.

### Milestone 7 — Automation

Configured hourly Security Watch report generation and automated Windows report pulling.

### Milestone 8 — Restart Recovery

Configured scheduled tasks and service startup workflows.

### Milestone 9 — Maintenance Mode

Added planned maintenance support to prevent expected outages from being treated as incidents.

### Milestone 10 — Reliability Metrics

Added 24-hour uptime and 7-day reliability reporting based on PostgreSQL history.

---

## Example Workflow

A normal LabWatch workflow looks like this:

```text
1. Services are checked from the Windows LabWatch host.
2. Results are displayed on the dashboard.
3. Results are saved to PostgreSQL.
4. If a service changes state, an incident is recorded.
5. If a service is in Maintenance Mode, it is excluded from normal incident handling.
6. Security Watch runs hourly on Ubuntu.
7. Windows pulls the latest report automatically.
8. The /security page displays the newest report.
9. The /reliability page shows uptime and problem counts.
```

---

## Future Improvements

Planned or possible future improvements:

* CSV export for history and incidents
* Email alerts for new incidents
* Security Watch report sections split into visual cards
* Service grouping by category
* Per-service detail pages
* Backup status page
* PostgreSQL backup automation display
* Authentication for the LabWatch dashboard
* Dark/light theme toggle
* API endpoint for service health
* Dockerized LabWatch deployment

---

## Repository Structure

Example structure:

```text
LabWatch/
├── app.py
├── db.py
├── security_watch.py
├── services.yml
├── start_labwatch.ps1
├── pull_security_report.ps1
├── requirements.txt
├── README.md
├── .gitignore
├── docs/
│   ├── architecture.md
│   ├── scheduled-task-labwatch-pull.xml
│   └── scheduled-task-start-labwatch.xml
├── screenshots/
│   ├── labwatch-dashboard-21-online.png
│   ├── labwatch-history-page.png
│   ├── labwatch-incidents-page.png
│   ├── labwatch-security-watch-npm-logs.png
│   ├── labwatch-maintenance-mode.png
│   └── labwatch-reliability-page.png
├── templates/
│   ├── index.html
│   ├── history.html
│   ├── incidents.html
│   ├── security.html
│   ├── maintenance.html
│   └── reliability.html
├── static/
│   └── style.css
└── security_reports/
    └── latest_security_report.txt
```

The `security_reports/` folder is ignored by Git because it contains generated report data.

---

## How to Run LabWatch Locally

From the Windows LabWatch host:

```powershell
cd D:\Scripts\LabWatch
.\venv\Scripts\Activate.ps1
python app.py
```

Open:

```text
http://127.0.0.1:5050
```

Or from another LAN device:

```text
http://192.168.10.50:5050
```

---

## How Security Watch Runs

On the Ubuntu server:

```bash
cd ~/Projects/homelab-security-watch
./run-security-watch-latest.sh
```

The latest report is saved as:

```text
reports/latest_security_report.txt
```

Windows pulls the report into LabWatch with:

```powershell
powershell -ExecutionPolicy Bypass -File D:\Scripts\LabWatch\pull_security_report.ps1
```

---

## Personal Learning Outcome

This project helped me practice real-world IT operations skills by building and maintaining a working monitoring platform instead of only reading about one.

The project required me to troubleshoot service failures, DNS issues, firewall behavior, Hyper-V virtual switching, PostgreSQL permissions, Docker volume paths, SSH authentication, scheduled tasks, cron jobs, and dashboard logic.

LabWatch is now a practical homelab command center that gives visibility into service health, incidents, maintenance, security reports, and reliability.

---

## Status

Current project status:

```text
Functional
Documented
Automated
Expanded with Maintenance Mode
Expanded with Reliability Metrics
Ready for continued improvement
```

---

## Author

Created by Nicholas Deno as part of a hands-on IT homelab and infrastructure portfolio project.
