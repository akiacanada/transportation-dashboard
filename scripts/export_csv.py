import sqlite3
import csv
import os

DB_PATH = "data/transportation.db"
EXPORT_DIR = "data/exports"

os.makedirs(EXPORT_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

def export(query, filename):
    cursor.execute(query)
    columns = [d[0] for d in cursor.description]
    rows = cursor.fetchall()
    path = os.path.join(EXPORT_DIR, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {path}")

export("SELECT * FROM shipments", "shipments.csv")
export("SELECT * FROM carriers", "carriers.csv")
export("""
    SELECT l.lane_id, l.origin_warehouse, w.city AS origin_city, w.state AS origin_state,
           l.inland_hub_airport, l.connection_airport, l.destination_airport,
           l.destination_city, l.destination_country, l.lane_type, l.standard_transit_days
    FROM lanes l
    JOIN warehouses w ON w.warehouse_id = l.origin_warehouse
""", "lanes.csv")

conn.close()