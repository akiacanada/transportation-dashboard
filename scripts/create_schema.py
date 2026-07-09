import sqlite3
import os

DB_PATH = os.path.join("data", "transportation.db")

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

cursor.executescript("""
DROP TABLE IF EXISTS shipments;
DROP TABLE IF EXISTS lanes;
DROP TABLE IF EXISTS carriers;
DROP TABLE IF EXISTS warehouses;

CREATE TABLE warehouses (
    warehouse_id   TEXT PRIMARY KEY,
    warehouse_name TEXT NOT NULL,
    city           TEXT NOT NULL,
    state          TEXT NOT NULL
);

CREATE TABLE carriers (
    carrier_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    carrier_name TEXT NOT NULL,
    carrier_type TEXT NOT NULL,
    region       TEXT
);

CREATE TABLE lanes (
    lane_id                INTEGER PRIMARY KEY AUTOINCREMENT,
    origin_warehouse       TEXT NOT NULL,
    inland_hub_airport     TEXT,
    connection_airport     TEXT,
    destination_airport    TEXT,
    destination_city       TEXT NOT NULL,
    destination_country    TEXT NOT NULL,
    lane_type              TEXT NOT NULL,
    standard_transit_days  INTEGER NOT NULL,
    FOREIGN KEY (origin_warehouse) REFERENCES warehouses(warehouse_id)
);

CREATE TABLE shipments (
    shipment_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    lane_id                 INTEGER NOT NULL,
    carrier_id              INTEGER NOT NULL,
    shipment_mode            TEXT NOT NULL,
    pickup_date              TEXT NOT NULL,
    promised_delivery_date   TEXT NOT NULL,
    delivery_date            TEXT,
    weight_lbs                REAL NOT NULL,
    freight_cost               REAL NOT NULL,
    shipment_status           TEXT NOT NULL,
    delay_reason              TEXT,
    FOREIGN KEY (lane_id) REFERENCES lanes(lane_id),
    FOREIGN KEY (carrier_id) REFERENCES carriers(carrier_id)
);
""")

# --- Seed reference data ---

warehouses = [
    ("WH01", "Austin DC",   "Austin",    "TX"),
    ("WH02", "Phoenix DC",  "Phoenix",   "AZ"),
    ("WH03", "San Jose DC", "San Jose",  "CA"),
    ("WH04", "Portland DC", "Portland",  "OR"),
    ("WH05", "Raleigh DC",  "Raleigh",   "NC"),
]
cursor.executemany(
    "INSERT INTO warehouses VALUES (?, ?, ?, ?)", warehouses
)

carriers = [
    ("FedEx Freight",     "LTL",               "National"),
    ("UPS Supply Chain",  "Parcel",            "National"),
    ("DHL",               "International Air", "Global"),
    ("XPO Logistics",     "LTL",               "National"),
    ("Estes",             "LTL",               "National"),
    ("Old Dominion",      "LTL",               "National"),
    ("Saia",              "LTL",               "Regional"),
    ("TForce Freight",    "LTL",               "National"),
]
cursor.executemany(
    "INSERT INTO carriers (carrier_name, carrier_type, region) VALUES (?, ?, ?)",
    carriers
)

# DRAFT lane list — replace with your own routing knowledge
# columns: origin_warehouse, inland_hub_airport, connection_airport,
#          destination_airport, destination_city, destination_country,
#          lane_type, standard_transit_days
lanes = [
    ("WH01", None,  None,  "DAL", "Dallas",       "USA",       "Domestic Truck",    1),
    ("WH01", None,  None,  "HOU", "Houston",      "USA",       "Domestic Truck",    1),
    ("WH01", None,  None,  "RDU", "Raleigh",      "USA",       "Domestic Truck",    4),
    ("WH02", None,  None,  "PHX", "Tucson",       "USA",       "Domestic Truck",    1),
    ("WH03", None,  None,  "SMF", "Sacramento",   "USA",       "Domestic Truck",    1),
    ("WH04", None,  None,  "SEA", "Seattle",      "USA",       "Domestic Truck",    1),
    ("WH05", None,  None,  "CLT", "Charlotte",    "USA",       "Domestic Truck",    1),
    ("WH03", None,  None,  "RDU", "Raleigh",      "USA",       "Domestic Truck",    7),
    ("WH02", None,  None,  "PDX", "Portland",     "USA",       "Domestic Truck",    3),
    ("WH01", "IAH", None,  "NRT", "Tokyo",        "Japan",     "International Air", 4),
    ("WH01", "IAH", "FRA", "SIN", "Singapore",    "Singapore", "International Air", 6),
    ("WH03", "LAX", None,  "TPE", "Taipei",       "Taiwan",    "International Air", 4),
    ("WH03", "LAX", None,  "ICN", "Seoul",        "South Korea","International Air",4),
    ("WH02", "LAX", None,  "PVG", "Shanghai",     "China",     "International Air", 5),
    ("WH05", "ORD", "FRA", "KUL", "Kuala Lumpur", "Malaysia",  "International Air", 7),
    ("WH04", "LAX", None,  "PEN", "Penang",       "Malaysia",  "International Air", 6),
]
cursor.executemany(
    """INSERT INTO lanes
       (origin_warehouse, inland_hub_airport, connection_airport,
        destination_airport, destination_city, destination_country,
        lane_type, standard_transit_days)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
    lanes
)

conn.commit()
conn.close()

print("Schema created and seed data loaded:", DB_PATH)