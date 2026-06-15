import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from db import get_db_connection


def load_inventory(json_path):
    with open(json_path, "r", encoding="utf-8-sig") as file:
        return json.load(file)


def import_inventory(inventory):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO asset_inventory (
            hostname,
            ip_address,
            operating_system,
            os_version,
            pending_updates,
            pending_security_updates,
            last_boot_time,
            uptime_days,
            disk_total_gb,
            disk_free_gb,
            compliance_status,
            scan_source,
            scanned_at
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (hostname)
        DO UPDATE SET
            ip_address = EXCLUDED.ip_address,
            operating_system = EXCLUDED.operating_system,
            os_version = EXCLUDED.os_version,
            pending_updates = EXCLUDED.pending_updates,
            pending_security_updates = EXCLUDED.pending_security_updates,
            last_boot_time = EXCLUDED.last_boot_time,
            uptime_days = EXCLUDED.uptime_days,
            disk_total_gb = EXCLUDED.disk_total_gb,
            disk_free_gb = EXCLUDED.disk_free_gb,
            compliance_status = EXCLUDED.compliance_status,
            scan_source = EXCLUDED.scan_source,
            scanned_at = EXCLUDED.scanned_at
        """,
        (
            inventory.get("hostname"),
            inventory.get("ip_address"),
            inventory.get("operating_system"),
            inventory.get("os_version"),
            inventory.get("pending_updates", 0),
            inventory.get("pending_security_updates", 0),
            inventory.get("last_boot_time"),
            inventory.get("uptime_days"),
            inventory.get("disk_total_gb"),
            inventory.get("disk_free_gb"),
            inventory.get("compliance_status", "Unknown"),
            inventory.get("scan_source"),
            inventory.get("scanned_at"),
        ),
    )

    cursor.execute(
        """
        INSERT INTO patch_scan_history (
            hostname,
            operating_system,
            pending_updates,
            pending_security_updates,
            compliance_status,
            notes,
            scanned_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            inventory.get("hostname"),
            inventory.get("operating_system"),
            inventory.get("pending_updates", 0),
            inventory.get("pending_security_updates", 0),
            inventory.get("compliance_status", "Unknown"),
            inventory.get("update_scan_status"),
            inventory.get("scanned_at"),
        ),
    )

    connection.commit()
    cursor.close()
    connection.close()


if __name__ == "__main__":
    inventory_directory = Path(
        r"D:\Scripts\LabWatch\patchwatch\data"
    )

    inventory_files = sorted(
        inventory_directory.glob("*.json")
    )

    if not inventory_files:
        raise FileNotFoundError(
            f"No inventory JSON files found in {inventory_directory}"
        )

    for inventory_file in inventory_files:
        inventory_data = load_inventory(inventory_file)
        import_inventory(inventory_data)

        print(
            f"Imported PatchWatch inventory for "
            f"{inventory_data.get('hostname')} "
            f"from {inventory_file.name}"
        )