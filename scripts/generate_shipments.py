import sqlite3
import random
from datetime import date, timedelta

DB_PATH = "data/transportation.db"
NUM_SHIPMENTS = 20000

# Anchor the window to "today" so re-running this later still makes sense —
# DATA_END always represents "as of when this was generated."
DATA_END = date.today()
DATA_START = DATA_END - timedelta(days=730)

random.seed(42)  # fixed seed = reproducible dataset while we're iterating/debugging

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

cursor.execute("DELETE FROM shipments")  # makes this script safely re-runnable

# --- Load reference data from the tables we already built ---
lanes = cursor.execute(
    "SELECT lane_id, origin_warehouse, lane_type, standard_transit_days FROM lanes"
).fetchall()
carriers = cursor.execute(
    "SELECT carrier_id, carrier_name, carrier_type FROM carriers"
).fetchall()

# --- Business rules ---

CARRIER_ON_TIME_RATE = {
    "Old Dominion": 0.98,
    "Estes": 0.96,
    "FedEx Freight": 0.95,
    "DHL": 0.94,
    "UPS Supply Chain": 0.93,
    "XPO Logistics": 0.89,
    "Saia": 0.87,
    "TForce Freight": 0.84,
}

DOMESTIC_CARRIERS = [c for c in carriers if c[2] == "LTL"]
INTL_CARRIERS = [c for c in carriers if c[2] in ("International Air", "Parcel")]

MODE_SPECS = {
    "Parcel": {"weight": (5, 75),       "cost": (25, 150)},
    "LTL":    {"weight": (250, 5000),   "cost": (300, 2000)},
    "FTL":    {"weight": (8000, 42000), "cost": (1200, 4500)},
    "Air":    {"weight": (50, 2000),    "cost": (500, 9000)},
}

DOMESTIC_MODE_WEIGHTS = {"LTL": 60, "FTL": 25, "Parcel": 15}

DOMESTIC_DELAY_REASONS = {
    "Weather": 30, "Mechanical Issue": 18, "Warehouse Delay": 16,
    "Capacity Constraint": 16, "Driver Shortage": 10,
    "Customer Delay": 7, "Other": 3,
}
INTL_DELAY_REASONS = {
    "Customs Hold": 35, "Weather": 15, "Capacity Constraint": 15,
    "Mechanical Issue": 10, "Incorrect Documentation": 15,
    "Customer Delay": 5, "Other": 5,
}

LANE_WEIGHT = {"Domestic Truck": 10, "International Air": 3}  # domestic runs far more often

MONTH_SEASONALITY = {
    1: 0.8, 2: 0.8, 3: 0.9, 4: 1.0, 5: 1.0, 6: 1.0,
    7: 0.9, 8: 0.9, 9: 1.0, 10: 1.1, 11: 1.3, 12: 1.4,
}

CANCEL_RATE = 0.015

STUCK_IN_TRANSIT_RATE = 0.008  # ~0.8% of otherwise-completed shipments go "stuck" — overdue, still open

# --- Fiscal quarter-end crunch (fiscal year starts November) ---
# Quarters close end of Jan / Apr / Jul / Oct. The last stretch before each
# close sees a volume spike and worse on-time performance as everyone
# pushes to hit revenue.
QUARTER_END_WINDOW_DAYS = 10
QUARTER_END_VOLUME_MULTIPLIER = 2.5
QUARTER_END_ON_TIME_PENALTY = 0.85   # carriers hit their on-time rate 15% less often
CAPACITY_BOOST_IN_CRUNCH = 3         # "Capacity Constraint" 3x more likely as a delay reason

FISCAL_QUARTER_ENDS = [(1, 31), (4, 30), (7, 31), (10, 31)]

def fiscal_quarter_end_date(d):
    for month, day in FISCAL_QUARTER_ENDS:
        candidate = date(d.year, month, day)
        if d <= candidate:
            return candidate
    # d is in Nov or Dec — its quarter closes in January of next year
    return date(d.year + 1, 1, 31)

def is_quarter_end_crunch(d):
    q_end = fiscal_quarter_end_date(d)
    return q_end - timedelta(days=QUARTER_END_WINDOW_DAYS) <= d <= q_end

# --- Precompute a pickup-date pool weighted by seasonality + quarter-end crunch ---
all_dates = []
d = DATA_START
while d <= DATA_END:
    all_dates.append(d)
    d += timedelta(days=1)

date_weights = [
    MONTH_SEASONALITY[dt.month] * (QUARTER_END_VOLUME_MULTIPLIER if is_quarter_end_crunch(dt) else 1.0)
    for dt in all_dates
]
pickup_dates = random.choices(all_dates, weights=date_weights, k=NUM_SHIPMENTS)

lane_weights = [LANE_WEIGHT[l[2]] for l in lanes]

# --- Generate each shipment ---
rows = []
for i in range(NUM_SHIPMENTS):
    lane_id, origin_warehouse, lane_type, transit_days = random.choices(
        lanes, weights=lane_weights, k=1
    )[0]

    carrier_pool = INTL_CARRIERS if lane_type == "International Air" else DOMESTIC_CARRIERS
    carrier_id, carrier_name, carrier_type = random.choice(carrier_pool)

    pickup_date = pickup_dates[i]
    promised_delivery_date = pickup_date + timedelta(days=transit_days)
    in_crunch = is_quarter_end_crunch(pickup_date)

    if lane_type == "International Air":
        mode = "Air"
    else:
        mode = random.choices(
            list(DOMESTIC_MODE_WEIGHTS.keys()),
            weights=list(DOMESTIC_MODE_WEIGHTS.values()), k=1
        )[0]

    w_lo, w_hi = MODE_SPECS[mode]["weight"]
    c_lo, c_hi = MODE_SPECS[mode]["cost"]
    weight_lbs = round(random.uniform(w_lo, w_hi), 1)
    freight_cost = round(random.uniform(c_lo, c_hi), 2)

    if promised_delivery_date > DATA_END:
        # picked up too recently to have arrived yet
        status = "In Transit"
        delivery_date = None
        delay_reason = None
     elif random.random() < STUCK_IN_TRANSIT_RATE:
        # "lost" in transit — already overdue, still unresolved
        status = "In Transit"
        delivery_date = None
        delay_reason = None
    elif random.random() < CANCEL_RATE:
    else:
        effective_on_time_rate = CARRIER_ON_TIME_RATE[carrier_name]
        if in_crunch:
            effective_on_time_rate *= QUARTER_END_ON_TIME_PENALTY
        on_time = random.random() < effective_on_time_rate

        if on_time:
            # never let "early" push delivery before pickup
            early_days = random.randint(0, min(2, transit_days))
            delivery_date = promised_delivery_date - timedelta(days=early_days)
            delay_reason = None
        else:
            reason_pool = dict(INTL_DELAY_REASONS if lane_type == "International Air" else DOMESTIC_DELAY_REASONS)
            if in_crunch:
                reason_pool["Capacity Constraint"] *= CAPACITY_BOOST_IN_CRUNCH
            delay_reason = random.choices(
                list(reason_pool.keys()), weights=list(reason_pool.values()), k=1
            )[0]
            days_late = random.randint(1, 8 if lane_type == "International Air" else 5)
            delivery_date = promised_delivery_date + timedelta(days=days_late)
        status = "Delivered"

    rows.append((
        lane_id, carrier_id, mode,
        pickup_date.isoformat(),
        promised_delivery_date.isoformat(),
        delivery_date.isoformat() if delivery_date else None,
        weight_lbs, freight_cost, status, delay_reason,
    ))

cursor.executemany("""
    INSERT INTO shipments
    (lane_id, carrier_id, shipment_mode, pickup_date, promised_delivery_date,
     delivery_date, weight_lbs, freight_cost, shipment_status, delay_reason)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", rows)

conn.commit()
conn.close()

print(f"Generated {NUM_SHIPMENTS} shipments from {DATA_START} to {DATA_END}.")