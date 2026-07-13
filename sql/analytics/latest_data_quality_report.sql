SELECT
    check_date,
    total_raw_rows,
    duplicate_order_ids,
    null_amount_count,
    negative_amount_count,
    null_city_count,
    accepted_rows,
    rejected_rows,
    data_quality_score
FROM etl_db.dq_orders_report
ORDER BY calculated_at DESC
LIMIT 5;
