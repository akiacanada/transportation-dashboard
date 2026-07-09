.headers on
.mode column

-- Overall delay reason breakdown
SELECT delay_reason,
       COUNT(*) AS occurrences,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM shipments WHERE delay_reason IS NOT NULL), 1) AS pct_of_delays
FROM shipments
WHERE delay_reason IS NOT NULL
GROUP BY delay_reason
ORDER BY occurrences DESC;

-- Days-late distribution (bucketed)
SELECT days_late_bucket, COUNT(*) AS shipments
FROM (
  SELECT
    CASE
      WHEN delivery_date <= promised_delivery_date THEN '0 (on-time)'
      WHEN julianday(delivery_date) - julianday(promised_delivery_date) <= 2 THEN '1-2 days late'
      WHEN julianday(delivery_date) - julianday(promised_delivery_date) <= 4 THEN '3-4 days late'
      WHEN julianday(delivery_date) - julianday(promised_delivery_date) <= 6 THEN '5-6 days late'
      ELSE '7+ days late'
    END AS days_late_bucket,
    CASE
      WHEN delivery_date <= promised_delivery_date THEN 0
      WHEN julianday(delivery_date) - julianday(promised_delivery_date) <= 2 THEN 1
      WHEN julianday(delivery_date) - julianday(promised_delivery_date) <= 4 THEN 2
      WHEN julianday(delivery_date) - julianday(promised_delivery_date) <= 6 THEN 3
      ELSE 4
    END AS sort_order
  FROM shipments
  WHERE shipment_status = 'Delivered'
)
GROUP BY days_late_bucket, sort_order
ORDER BY sort_order;

-- Highest-risk carrier + lane combinations (min 20 shipments to be meaningful)
SELECT c.carrier_name,
       w.city || ' -> ' || l.destination_city AS lane,
       COUNT(*) AS shipments,
       ROUND(100.0 * SUM(CASE WHEN s.delivery_date > s.promised_delivery_date THEN 1 ELSE 0 END) / COUNT(*), 1) AS delay_rate_pct
FROM shipments s
JOIN carriers c ON c.carrier_id = s.carrier_id
JOIN lanes l ON l.lane_id = s.lane_id
JOIN warehouses w ON w.warehouse_id = l.origin_warehouse
WHERE s.shipment_status = 'Delivered'
GROUP BY c.carrier_name, lane
HAVING COUNT(*) >= 20
ORDER BY delay_rate_pct DESC
LIMIT 10;

-- Open, currently-overdue shipments needing attention
SELECT s.shipment_id,
       c.carrier_name,
       w.city || ' -> ' || l.destination_city AS lane,
       s.pickup_date,
       s.promised_delivery_date,
       CAST(julianday('now') - julianday(s.promised_delivery_date) AS INTEGER) AS days_overdue
FROM shipments s
JOIN carriers c ON c.carrier_id = s.carrier_id
JOIN lanes l ON l.lane_id = s.lane_id
JOIN warehouses w ON w.warehouse_id = l.origin_warehouse
WHERE s.shipment_status = 'In Transit'
  AND s.promised_delivery_date < DATE('now')
ORDER BY days_overdue DESC;