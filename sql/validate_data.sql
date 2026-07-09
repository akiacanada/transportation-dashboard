.headers on
.mode column

-- 1. Status breakdown — should be mostly Delivered, a slice In Transit, tiny sliver Cancelled
SELECT shipment_status, COUNT(*) AS n,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM shipments), 1) AS pct
FROM shipments
GROUP BY shipment_status;

-- 2. Overall on-time delivery rate (Delivered only)
SELECT ROUND(100.0 * SUM(CASE WHEN delivery_date <= promised_delivery_date THEN 1 ELSE 0 END) / COUNT(*), 2) AS otd_pct
FROM shipments
WHERE shipment_status = 'Delivered';

-- 3. On-time rate by carrier — should roughly match the input rates
--    (Old Dominion ~98%, Estes ~96%, FedEx ~95%, DHL ~94%, UPS ~93%, XPO ~89%, Saia ~87%, TForce ~84%)
SELECT c.carrier_name,
       COUNT(*) AS shipments,
       ROUND(100.0 * SUM(CASE WHEN s.delivery_date <= s.promised_delivery_date THEN 1 ELSE 0 END) / COUNT(*), 1) AS otd_pct
FROM shipments s
JOIN carriers c ON c.carrier_id = s.carrier_id
WHERE s.shipment_status = 'Delivered'
GROUP BY c.carrier_name
ORDER BY otd_pct DESC;

-- 4. Any impossible dates? delivery before pickup should be ZERO rows
SELECT COUNT(*) AS impossible_deliveries
FROM shipments
WHERE delivery_date IS NOT NULL AND delivery_date < pickup_date;

-- 5. Weight/cost ranges by mode — should fall inside the ranges we defined
SELECT shipment_mode,
       MIN(weight_lbs) AS min_wt, MAX(weight_lbs) AS max_wt,
       MIN(freight_cost) AS min_cost, MAX(freight_cost) AS max_cost,
       COUNT(*) AS n
FROM shipments
GROUP BY shipment_mode;

-- 6. delay_reason should be NULL exactly when NOT late, and set exactly when late
SELECT
  SUM(CASE WHEN shipment_status = 'Delivered' AND delivery_date > promised_delivery_date AND delay_reason IS NULL THEN 1 ELSE 0 END) AS late_missing_reason,
  SUM(CASE WHEN shipment_status = 'Delivered' AND delivery_date <= promised_delivery_date AND delay_reason IS NOT NULL THEN 1 ELSE 0 END) AS ontime_has_reason
FROM shipments;

-- 7. Monthly volume — Nov/Dec should be visibly higher (seasonality check)
SELECT strftime('%m', pickup_date) AS month, COUNT(*) AS shipments
FROM shipments
GROUP BY month
ORDER BY month;

-- 8. Domestic vs international volume split — domestic should dominate
SELECT l.lane_type, COUNT(*) AS shipments,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM shipments), 1) AS pct
FROM shipments s
JOIN lanes l ON l.lane_id = s.lane_id
GROUP BY l.lane_type;