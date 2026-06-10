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