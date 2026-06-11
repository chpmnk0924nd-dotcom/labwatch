# LabWatch Architecture

## Main Components

- Windows Host: Runs LabWatch Flask dashboard
- FreeBSD Server: Runs PostgreSQL database for history and incidents
- Ubuntu Server: Runs Security Watch and generates hourly reports
- Windows Server DC01: Provides DNS, LDAP, and Active Directory services
- Proxmox: Virtualization platform
- OPNsense: Firewall/router
- Nginx Proxy Manager: Reverse proxy and access log source
- Wazuh/CrowdSec: Security monitoring tools

## Data Flow

1. LabWatch checks all services from the Windows host.
2. Service results are written to PostgreSQL on FreeBSD.
3. Status changes are written to the incidents table.
4. Security Watch runs hourly on Ubuntu.
5. Windows pulls the latest Security Watch report by SCP.
6. LabWatch displays the latest report at `/security`.