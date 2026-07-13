SELECT
    count() AS total_raw_rows,
    countIf(amount IS NULL) AS null_amount_count,
    countIf(amount < 0) AS negative_amount_count,
    countIf(city = '') AS empty_city_count,
    countIf(status != 'completed') AS not_completed_orders
FROM etl_db.bronze_orders_raw;
