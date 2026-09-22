# Transportation Intelligence Dashboard

A logistics analytics project built around a simulated transportation operation — semiconductor equipment shipped from five U.S. distribution centers to domestic and international destinations. Modeled the data, wrote the SQL logic behind the KPIs, and built a Tableau dashboard to surface carrier performance, lane issues, and delay trends for logistics decision-making.

## Business question

How can logistics coordinators quickly identify late shipments, underperforming carriers, and rising transportation costs — before they become recurring operational problems?

## Live dashboard

**[View the interactive dashboard on Tableau Public →](TABLEAU_PUBLIC_LINK_HERE)**

## Data model

A normalized SQLite database with four tables:

- **`warehouses`** — 5 origin distribution centers (Austin, Phoenix, San Jose, Portland, Raleigh)
- **`carriers`** — 8 carriers spanning LTL, Parcel, and International Air, each with a distinct on-time reliability rate
- **`lanes`** — 16 origin → destination routes, domestic truck and international air (including multi-airport routing through inland hubs like IAH/LAX/ORD and international connections)
- **`shipments`** — ~20,000 simulated shipment records, generated with business rules rather than pure randomness (see below)

## What makes the data realistic, not random

- **Carrier reliability is modeled**, not uniform — each carrier has its own on-time rate (80.8%–95.3%), pulled from realistic industry-style benchmarks.
- **Fiscal quarter-end congestion**: the simulated company runs a November-start fiscal year (quarters close end of Jan/Apr/Jul/Oct). Shipment volume spikes ~2.5x in the last 10 days of each quarter, and on-time performance drops as carrier capacity gets strained — a pattern clearly visible in the Executive Overview trend chart.
- **Delay reasons differ by geography** — international lanes see Customs Hold and Documentation issues; domestic lanes see Weather, Mechanical, and Driver Shortage issues.
- **Seasonality**: holiday-season volume (Nov/Dec) is weighted higher, compounding with the fiscal quarter-end effect.
- **Open/stuck shipments**: a small fraction of recent shipments are modeled as still in-transit and already overdue, representing real operational visibility gaps.

## Dashboard pages

1. **Executive Overview** — total shipments, on-time %, avg transit days, delayed count, freight spend, cost per shipment, and a month-over-month trend showing the fiscal quarter-end pattern. *(Live)*
2. **Carrier Performance** — carrier ranking by on-time %, transit days, delay counts, freight cost, and volume share. *(SQL complete, Tableau build in progress)*
3. **Lane / Route Analysis** — lane-level performance, slowest lanes, most expensive lanes, delay rate by lane. *(SQL complete, Tableau build in progress)*
4. **Delay Intelligence** — delay reason breakdown, days-late distribution, highest-risk carrier/lane combinations, and open shipments needing attention. *(SQL complete, Tableau build in progress)*

## Tech stack

- **Python** (`sqlite3`, `random`, `datetime`) — schema creation and the shipment data generator
- **SQLite** — normalized relational database
- **SQL** — 20+ queries covering executive KPIs, carrier scorecards, lane analysis, and delay intelligence (see `sql/`)
- **Tableau** — interactive dashboard, connected via CSV export (see `scripts/export_csv.py`)

## Repo structure

```
scripts/     Python: schema creation, data generation, CSV export
sql/         SQL queries and validation checks, organized by dashboard page
data/        SQLite database and CSV exports for Tableau
tableau/     Tableau workbook (.twb)
docs/        Screenshots and supporting documentation
```

## Reproducing this project

```bash
python scripts/create_schema.py       # creates tables, seeds warehouses/carriers/lanes
python scripts/generate_shipments.py  # generates ~20,000 realistic shipment records
python scripts/export_csv.py          # exports to CSV for Tableau
```

Validation and KPI queries can be run directly against the SQLite database, e.g.:

```bash
sqlite3 data/transportation.db < sql/validate_data.sql
sqlite3 data/transportation.db < sql/executive_overview.sql
```
