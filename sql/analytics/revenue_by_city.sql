SELECT
    city,
    count() AS total_orders,
    round(sum(amount), 2) AS total_revenue,
    round(avg(amount), 2) AS avg_order_value
FROM etl_db.silver_orders_clean
GROUP BY city
ORDER BY total_revenue DESC;
