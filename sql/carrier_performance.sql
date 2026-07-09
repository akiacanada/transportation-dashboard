.headers on
.mode column

-- Carrier scorecard: ranking, on-time %, avg transit, delay count
SELECT c.carrier_name,
       c.carrier_type,
       COUNT(*) AS shipments,
       ROUND(100.0 * SUM(CASE WHEN s.delivery_date <= s.promised_delivery_date THEN 1 ELSE 0 END) / COUNT(*), 1) AS on_time_pct,
       ROUND(AVG(julianday(s.delivery_date) - julianday(s.pickup_date)), 2) AS avg_transit_days,
       SUM(CASE WHEN s.delivery_date > s.promised_delivery_date THEN 1 ELSE 0 END) AS delayed_shipments
FROM shipments s
JOIN carriers c ON c.carrier_id = s.carrier_id
WHERE s.shipment_status = 'Delivered'
GROUP BY c.carrier_name, c.carrier_type
ORDER BY on_time_pct DESC;

-- Freight cost by carrier
SELECT c.carrier_name,
       COUNT(*) AS shipments,
       ROUND(SUM(s.freight_cost), 2) AS total_freight_cost,
       ROUND(AVG(s.freight_cost), 2) AS avg_freight_cost
FROM shipments s
JOIN carriers c ON c.carrier_id = s.carrier_id
GROUP BY c.carrier_name
ORDER BY total_freight_cost DESC;

-- Carrier volume share
SELECT c.carrier_name,
       COUNT(*) AS shipments,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM shipments), 1) AS volume_share_pct
FROM shipments s
JOIN carriers c ON c.carrier_id = s.carrier_id
GROUP BY c.carrier_name
ORDER BY volume_share_pct DESC;

-- Delay reason breakdown by carrier
SELECT c.carrier_name,
       s.delay_reason,
       COUNT(*) AS occurrences
FROM shipments s
JOIN carriers c ON c.carrier_id = s.carrier_id
WHERE s.delay_reason IS NOT NULL
GROUP BY c.carrier_name, s.delay_reason
ORDER BY c.carrier_name, occurrences DESC;