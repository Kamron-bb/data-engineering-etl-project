SELECT
    order_date,
    total_orders,
    total_revenue,
    avg_order_value
FROM etl_db.gold_daily_revenue
ORDER BY order_date;
