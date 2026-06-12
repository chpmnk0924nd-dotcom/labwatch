from pathlib import Path
from datetime import datetime
import yaml


def load_backup_config(config_path="backups.yml"):
    with open(config_path, "r") as file:
        data = yaml.safe_load(file) or {}

    return data.get("backups", [])


def get_path_age_hours(path):
    item_path = Path(path)

    if not item_path.exists():
        return None

    modified_time = datetime.fromtimestamp(item_path.stat().st_mtime)
    age = datetime.now() - modified_time

    return round(age.total_seconds() / 3600, 2)


def check_backup_item(item):
    name = item.get("name", "Unknown Backup")
    category = item.get("category", "Uncategorized")
    backup_type = item.get("type", "local_file")
    path = item.get("path")
    max_age_hours = item.get("max_age_hours", 24)
    notes = item.get("notes", "")

    result = {
        "name": name,
        "category": category,
        "type": backup_type,
        "path": path,
        "max_age_hours": max_age_hours,
        "notes": notes,
        "exists": False,
        "age_hours": None,
        "status": "Missing",
        "status_note": "Backup path does not exist.",
    }

    if not path:
        result["status"] = "Missing"
        result["status_note"] = "No backup path configured."
        return result

    item_path = Path(path)

    if not item_path.exists():
        return result

    age_hours = get_path_age_hours(path)

    result["exists"] = True
    result["age_hours"] = age_hours

    if age_hours is None:
        result["status"] = "Warning"
        result["status_note"] = "Backup exists, but age could not be calculated."
    elif age_hours <= max_age_hours:
        result["status"] = "Healthy"
        result["status_note"] = f"Backup is current. Age: {age_hours} hours."
    else:
        result["status"] = "Warning"
        result["status_note"] = f"Backup is older than expected. Age: {age_hours} hours."

    return result


def get_backup_status():
    backup_items = load_backup_config()
    results = []

    for item in backup_items:
        results.append(check_backup_item(item))

    total = len(results)
    healthy = sum(1 for item in results if item["status"] == "Healthy")
    warning = sum(1 for item in results if item["status"] == "Warning")
    missing = sum(1 for item in results if item["status"] == "Missing")

    if total == 0:
        health_percent = 0
    else:
        health_percent = round((healthy / total) * 100)

    return {
        "backups": results,
        "total": total,
        "healthy": healthy,
        "warning": warning,
        "missing": missing,
        "health_percent": health_percent,
        "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }