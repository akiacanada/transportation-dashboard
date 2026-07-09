.headers on
.mode column

-- Total shipments (all statuses)
SELECT COUNT(*) AS total_shipments FROM shipments;

-- On-time delivery % (only meaningful for completed shipments)
SELECT ROUND(100.0 * SUM(CASE WHEN delivery_date <= promised_delivery_date THEN 1 ELSE 0 END) / COUNT(*), 2) AS on_time_pct
FROM shipments
WHERE shipment_status = 'Delivered';

-- Average transit days (actual, not promised)
SELECT ROUND(AVG(julianday(delivery_date) - julianday(pickup_date)), 2) AS avg_transit_days
FROM shipments
WHERE shipment_status = 'Delivered';

-- Delayed shipment count
SELECT COUNT(*) AS delayed_shipments
FROM shipments
WHERE shipment_status = 'Delivered' AND delivery_date > promised_delivery_date;

-- Total freight spend and cost per shipment
SELECT ROUND(SUM(freight_cost), 2) AS total_freight_spend,
       ROUND(SUM(freight_cost) / COUNT(*), 2) AS cost_per_shipment
FROM shipments;

-- Month-over-month trend: volume, on-time %, spend
SELECT strftime('%Y-%m', pickup_date) AS month,
       COUNT(*) AS shipments,
       ROUND(100.0 * SUM(CASE WHEN shipment_status = 'Delivered' AND delivery_date <= promised_delivery_date THEN 1 ELSE 0 END)
             / NULLIF(SUM(CASE WHEN shipment_status = 'Delivered' THEN 1 ELSE 0 END), 0), 1) AS on_time_pct,
       ROUND(SUM(freight_cost), 2) AS freight_spend
FROM shipments
GROUP BY month
ORDER BY month;