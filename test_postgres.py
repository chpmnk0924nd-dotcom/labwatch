import psycopg2

conn = psycopg2.connect(
    host="192.168.10.100",
    port=5432,
    dbname="labwatch",
    user="labwatch_user",
    password="Chpmnk0924"
)

cur = conn.cursor()

cur.execute("""
    INSERT INTO service_checks (service_name, status)
    VALUES (%s, %s)
""", ("LabWatch LAN Test", "online"))

conn.commit()

cur.execute("SELECT * FROM service_checks ORDER BY id DESC LIMIT 5;")
rows = cur.fetchall()

for row in rows:
    print(row)

cur.close()
conn.close()