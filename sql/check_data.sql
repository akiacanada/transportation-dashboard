.headers on
.mode column

SELECT COUNT(*) AS total_shipments FROM shipments;

SELECT
  CASE WHEN CAST(strftime('%d', pickup_date) AS INTEGER) >= 21
       AND strftime('%m', pickup_date) IN ('01','04','07','10')
       THEN 'quarter-end crunch' ELSE 'normal' END AS period,
  COUNT(*) AS shipments,
  ROUND(100.0 * SUM(CASE WHEN delay_reason IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_delayed
FROM shipments
WHERE shipment_status = 'Delivered'
GROUP BY period;