CREATE DATABASE IF NOT EXISTS etl_db;

CREATE TABLE IF NOT EXISTS etl_db.bronze_orders_raw
(
    order_id Int32,
    customer_id Int32,
    order_date Date,
    city String,
    amount Nullable(Float64),
    status String,
    source_system String DEFAULT 'python_generator',
    loaded_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(order_date)
ORDER BY (order_date, order_id);

CREATE TABLE IF NOT EXISTS etl_db.silver_orders_clean
(
    order_id Int32,
    customer_id Int32,
    order_date Date,
    city String,
    amount Float64,
    status String,
    amount_with_tax Float64,
    month String,
    loaded_at DateTime DEFAULT now()
)
ENGINE = ReplacingMergeTree(loaded_at)
PARTITION BY month
ORDER BY order_id;

CREATE TABLE IF NOT EXISTS etl_db.gold_daily_revenue
(
    order_date Date,
    total_orders UInt64,
    total_revenue Float64,
    avg_order_value Float64,
    calculated_at DateTime DEFAULT now()
)
ENGINE = ReplacingMergeTree(calculated_at)
ORDER BY order_date;

CREATE TABLE IF NOT EXISTS etl_db.dq_orders_report
(
    check_date Date,
    total_raw_rows UInt64,
    duplicate_order_ids UInt64,
    null_amount_count UInt64,
    negative_amount_count UInt64,
    null_city_count UInt64,
    accepted_rows UInt64,
    rejected_rows UInt64,
    data_quality_score Float64,
    calculated_at DateTime DEFAULT now()
)
ENGINE = MergeTree
ORDER BY check_date;
