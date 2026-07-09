.headers on
.mode column

-- Lane scorecard: performance by origin -> destination
SELECT w.city || ' -> ' || l.destination_city AS lane,
       l.lane_type,
       l.standard_transit_days,
       COUNT(*) AS shipments,
       ROUND(100.0 * SUM(CASE WHEN s.delivery_date <= s.promised_delivery_date THEN 1 ELSE 0 END) / COUNT(*), 1) AS on_time_pct,
       ROUND(AVG(julianday(s.delivery_date) - julianday(s.pickup_date)), 2) AS avg_transit_days,
       ROUND(AVG(s.freight_cost), 2) AS avg_freight_cost
FROM shipments s
JOIN lanes l ON l.lane_id = s.lane_id
JOIN warehouses w ON w.warehouse_id = l.origin_warehouse
WHERE s.shipment_status = 'Delivered'
GROUP BY lane, l.lane_type, l.standard_transit_days
ORDER BY shipments DESC;

-- Slowest 5 lanes by actual avg transit time
SELECT w.city || ' -> ' || l.destination_city AS lane,
       ROUND(AVG(julianday(s.delivery_date) - julianday(s.pickup_date)), 2) AS avg_transit_days,
       COUNT(*) AS shipments
FROM shipments s
JOIN lanes l ON l.lane_id = s.lane_id
JOIN warehouses w ON w.warehouse_id = l.origin_warehouse
WHERE s.shipment_status = 'Delivered'
GROUP BY lane
ORDER BY avg_transit_days DESC
LIMIT 5;

-- Most expensive 5 lanes by avg cost per shipment
SELECT w.city || ' -> ' || l.destination_city AS lane,
       ROUND(AVG(s.freight_cost), 2) AS avg_freight_cost,
       ROUND(SUM(s.freight_cost), 2) AS total_freight_cost,
       COUNT(*) AS shipments
FROM shipments s
JOIN lanes l ON l.lane_id = s.lane_id
JOIN warehouses w ON w.warehouse_id = l.origin_warehouse
GROUP BY lane
ORDER BY avg_freight_cost DESC
LIMIT 5;

-- Delay rate by lane (highest-risk lanes first)
SELECT w.city || ' -> ' || l.destination_city AS lane,
       COUNT(*) AS shipments,
       ROUND(100.0 * SUM(CASE WHEN s.delivery_date > s.promised_delivery_date THEN 1 ELSE 0 END) / COUNT(*), 1) AS delay_rate_pct
FROM shipments s
JOIN lanes l ON l.lane_id = s.lane_id
JOIN warehouses w ON w.warehouse_id = l.origin_warehouse
WHERE s.shipment_status = 'Delivered'
GROUP BY lane
ORDER BY delay_rate_pct DESC;

-- Shipment volume share by lane
SELECT w.city || ' -> ' || l.destination_city AS lane,
       COUNT(*) AS shipments,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM shipments), 1) AS volume_share_pct
FROM shipments s
JOIN lanes l ON l.lane_id = s.lane_id
JOIN warehouses w ON w.warehouse_id = l.origin_warehouse
GROUP BY lane
ORDER BY volume_share_pct DESC;