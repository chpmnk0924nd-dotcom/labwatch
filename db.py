import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("LABWATCH_DB_HOST"),
        port=os.getenv("LABWATCH_DB_PORT"),
        dbname=os.getenv("LABWATCH_DB_NAME"),
        user=os.getenv("LABWATCH_DB_USER"),
        password=os.getenv("LABWATCH_DB_PASSWORD"),
    )


def save_service_check(service):
    """
    Save one LabWatch service check result to PostgreSQL.
    """

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO service_checks
            (service_name, status, host, port, category, url, status_note)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                service.get("name"),
                service.get("overall_status"),
                service.get("host"),
                service.get("port"),
                service.get("category"),
                service.get("url"),
                service.get("status_note"),
            ),
        )

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        print(f"[DB ERROR] Could not save service check: {e}")

def get_recent_service_checks(limit=50):
    """
    Get recent LabWatch service check history from PostgreSQL.
    """

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                id,
                service_name,
                status,
                host,
                port,
                category,
                url,
                status_note,
                checked_at
            FROM service_checks
            ORDER BY id DESC
            LIMIT %s
            """,
            (limit,)
        )

        rows = cur.fetchall()

        cur.close()
        conn.close()

        history = []
        for row in rows:
            history.append({
                "id": row[0],
                "service_name": row[1],
                "status": row[2],
                "host": row[3],
                "port": row[4],
                "category": row[5],
                "url": row[6],
                "status_note": row[7],
                "checked_at": row[8],
            })

        return history

    except Exception as e:
        print(f"[DB ERROR] Could not fetch service history: {e}")
        return []

def get_last_service_status(service_name):
    """
    Get the most recent saved status for a service.
    """

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT status
            FROM service_checks
            WHERE service_name = %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (service_name,)
        )

        row = cur.fetchone()

        cur.close()
        conn.close()

        if row:
            return row[0]

        return None

    except Exception as e:
        print(f"[DB ERROR] Could not fetch last status for {service_name}: {e}")
        return None

def save_incident(service, old_status, new_status):
    """
    Save an incident when a service status changes.
    """

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        note = f"{service.get('name')} changed from {old_status} to {new_status}. {service.get('status_note')}"

        cur.execute(
            """
            INSERT INTO incidents
            (service_name, old_status, new_status, host, port, category, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                service.get("name"),
                old_status,
                new_status,
                service.get("host"),
                service.get("port"),
                service.get("category"),
                note,
            ),
        )

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        print(f"[DB ERROR] Could not save incident: {e}")

def get_recent_incidents(limit=50):
    """
    Get recent LabWatch incidents from PostgreSQL.
    """

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                id,
                service_name,
                old_status,
                new_status,
                host,
                port,
                category,
                note,
                created_at
            FROM incidents
            ORDER BY id DESC
            LIMIT %s
            """,
            (limit,)
        )

        rows = cur.fetchall()

        cur.close()
        conn.close()

        incidents = []
        for row in rows:
            incidents.append({
                "id": row[0],
                "service_name": row[1],
                "old_status": row[2],
                "new_status": row[3],
                "host": row[4],
                "port": row[5],
                "category": row[6],
                "note": row[7],
                "created_at": row[8],
            })

        return incidents

    except Exception as e:
        print(f"[DB ERROR] Could not fetch incidents: {e}")
        return []

def create_maintenance_window(service_name, reason, end_time=None):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO maintenance_windows (service_name, reason, end_time, active)
        VALUES (%s, %s, %s, TRUE)
        """,
        (service_name, reason, end_time),
    )

    conn.commit()
    cur.close()
    conn.close()


def get_active_maintenance_windows():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, service_name, reason, start_time, end_time, active, created_at
        FROM maintenance_windows
        WHERE active = TRUE
        ORDER BY created_at DESC
        """
    )

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return rows


def get_active_maintenance_for_service(service_name):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, service_name, reason, start_time, end_time, active, created_at
        FROM maintenance_windows
        WHERE service_name = %s
          AND active = TRUE
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (service_name,),
    )

    row = cur.fetchone()
    cur.close()
    conn.close()

    return row


def end_maintenance_window(maintenance_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE maintenance_windows
        SET active = FALSE
        WHERE id = %s
        """,
        (maintenance_id,),
    )

    conn.commit()
    cur.close()
    conn.close()


def get_service_uptime(service_name, hours=24):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT status
        FROM service_checks
        WHERE service_name = %s
          AND checked_at >= NOW() - (%s || ' hours')::INTERVAL
        """,
        (service_name, hours),
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    total_checks = len(rows)

    if total_checks == 0:
        return {
            "uptime_percent": None,
            "total_checks": 0,
            "online_checks": 0,
            "problem_checks": 0,
            "maintenance_checks": 0,
        }

    online_checks = 0
    problem_checks = 0
    maintenance_checks = 0

    for row in rows:
        status = row[0]

        if status == "Online":
            online_checks += 1
        elif status == "Maintenance":
            maintenance_checks += 1
        else:
            problem_checks += 1

    counted_checks = total_checks - maintenance_checks

    if counted_checks == 0:
        uptime_percent = 100.0
    else:
        uptime_percent = round((online_checks / counted_checks) * 100, 1)

    return {
        "uptime_percent": uptime_percent,
        "total_checks": total_checks,
        "online_checks": online_checks,
        "problem_checks": problem_checks,
        "maintenance_checks": maintenance_checks,
    }


def get_reliability_summary(hours=24):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT service_name, status
        FROM service_checks
        WHERE checked_at >= NOW() - (%s || ' hours')::INTERVAL
        ORDER BY service_name
        """,
        (hours,),
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    summary = {}

    for service_name, status in rows:
        if service_name not in summary:
            summary[service_name] = {
                "service_name": service_name,
                "total_checks": 0,
                "online_checks": 0,
                "problem_checks": 0,
                "maintenance_checks": 0,
                "uptime_percent": None,
            }

        summary[service_name]["total_checks"] += 1

        if status == "Online":
            summary[service_name]["online_checks"] += 1
        elif status == "Maintenance":
            summary[service_name]["maintenance_checks"] += 1
        else:
            summary[service_name]["problem_checks"] += 1

    for service in summary.values():
        counted_checks = service["total_checks"] - service["maintenance_checks"]

        if counted_checks == 0:
            service["uptime_percent"] = 100.0
        else:
            service["uptime_percent"] = round(
                (service["online_checks"] / counted_checks) * 100,
                1,
            )

    return sorted(summary.values(), key=lambda item: item["service_name"])


def get_asset_inventory():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            id,
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
        FROM asset_inventory
        ORDER BY hostname
        """
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows