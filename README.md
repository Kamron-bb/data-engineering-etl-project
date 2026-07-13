# Data Engineering ETL Project

Production-style Data Engineering project that demonstrates batch ETL, ClickHouse analytical warehouse design, medallion architecture, data quality reporting, analytics SQL queries, and automated unit testing.

## Project Overview

This project simulates an end-to-end data pipeline for order data.

The pipeline extracts raw order records, loads them into a Bronze layer, cleans and validates them into a Silver layer, and builds business-ready Gold analytics tables in ClickHouse.

It also includes a Data Quality reporting layer that tracks invalid records, duplicates, null values, rejected rows, accepted rows, and an overall data quality score.

## Architecture

```text
Raw order data
      ↓
Bronze layer: raw source records
      ↓
Silver layer: cleaned and validated orders
      ↓
Gold layer: business-ready revenue metrics
      ↓
Analytics SQL queries
      ↓
Data Quality report
```

## Tech Stack

- Python
- Pandas
- ClickHouse
- Docker / Docker Compose
- SQL
- Pytest
- GitHub Actions CI
- Kafka / Airflow concepts

## Project Structure

```text
.
├── src/
│   ├── batch/
│   │   ├── orders_clickhouse_pipeline.py
│   │   ├── orders_medallion_clickhouse_pipeline.py
│   │   └── orders_sqlite_pipeline.py
│   ├── common/
│   │   └── config.py
│   ├── transformations/
│   │   └── orders_transform.py
│   ├── analytics/
│   │   └── run_analytics_queries.py
│   └── streaming/
│       ├── producer.py
│       └── consumer.py
│
├── sql/
│   ├── ddl/
│   │   └── clickhouse_tables.sql
│   └── analytics/
│       ├── latest_data_quality_report.sql
│       ├── raw_data_quality_overview.sql
│       ├── revenue_by_city.sql
│       └── revenue_by_day.sql
│
├── tests/
│   └── test_orders_transform.py
│
├── dags/
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .github/
│   └── workflows/
│       └── python-ci.yml
└── README.md
```

## Data Warehouse Layers

### Bronze Layer

The Bronze layer stores raw source records with minimal changes.

It is used for:

- auditability
- debugging
- replaying pipeline logic
- reprocessing data
- investigating data quality issues

Table:

```text
etl_db.bronze_orders_raw
```

### Silver Layer

The Silver layer stores cleaned and standardized records.

Cleaning logic includes:

- removing duplicated order IDs
- removing rows with null amounts
- removing rows with negative amounts
- removing rows with empty or missing city values
- keeping only completed orders
- adding tax-adjusted amount
- adding reporting month

Table:

```text
etl_db.silver_orders_clean
```

### Gold Layer

The Gold layer stores business-ready aggregated metrics.

Current Gold table:

```text
etl_db.gold_daily_revenue
```

Metrics:

- total orders
- total revenue
- average order value

## Data Quality

The project includes a dedicated Data Quality report table:

```text
etl_db.dq_orders_report
```

It tracks:

- total raw rows
- duplicate order IDs
- null amount count
- negative amount count
- null city count
- accepted rows
- rejected rows
- data quality score

This makes the pipeline more observable and helps identify data issues before they affect reporting or analytics.

## Analytics SQL Layer

The project includes reusable SQL queries for business and operational analysis.

Available queries:

```text
sql/analytics/latest_data_quality_report.sql
sql/analytics/raw_data_quality_overview.sql
sql/analytics/revenue_by_city.sql
sql/analytics/revenue_by_day.sql
```

These queries help answer questions such as:

- What is the daily revenue?
- Which cities generate the most revenue?
- How many records were rejected during data cleaning?
- What is the current data quality score?
- How many raw records contain null, negative, or invalid values?

## How to Run

### 1. Create and activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start ClickHouse

```bash
docker compose up -d
```

### 4. Run the medallion pipeline

```bash
python -m src.batch.orders_medallion_clickhouse_pipeline
```

Expected output:

```text
ClickHouse tables are ready.
Inserted rows into etl_db.bronze_orders_raw.
Inserted rows into etl_db.silver_orders_clean.
Inserted rows into etl_db.gold_daily_revenue.
Inserted rows into etl_db.dq_orders_report.
Pipeline finished successfully.
```

### 5. Run analytics queries

```bash
python -m src.analytics.run_analytics_queries
```

### 6. Run unit tests

```bash
PYTHONPATH=. pytest -q
```

Expected output:

```text
3 passed
```

## Configuration

The project uses environment variables for configuration.

Example configuration is stored in:

```text
.env.example
```

Variables:

## Local Services

After starting Docker Compose, the local services are available at:

```text
ClickHouse HTTP endpoint: http://localhost:8123
Airflow UI:              http://localhost:8080
Kafka broker:            localhost:9092
```

```env
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8123
CLICKHOUSE_DB=etl_db
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=clickhouse123

KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=orders_stream
```

For local development, create a `.env` file if needed. The `.env` file should not be committed to Git.

## Testing

The transformation logic is tested with Pytest.

Current tests cover:

- duplicate removal
- null amount filtering
- negative amount filtering
- empty city filtering
- completed order filtering
- tax calculation
- month calculation
- Data Quality metric calculation
- Gold revenue aggregation

Run tests:

```bash
PYTHONPATH=. pytest -q
```

## CI/CD

The project includes GitHub Actions CI.

The CI pipeline installs dependencies and runs unit tests automatically on push and pull request.

Workflow file:

```text
.github/workflows/python-ci.yml
```

## What This Project Demonstrates

This project demonstrates practical Data Engineering skills:

- end-to-end ETL pipeline development
- ClickHouse analytical warehouse design
- Bronze / Silver / Gold medallion architecture
- data quality and observability concepts
- SQL analytics layer
- Python transformation testing
- Docker-based local data platform
- CI pipeline with GitHub Actions
- production-style project structure
- separation of configuration, transformation, analytics and pipeline logic

## Future Improvements

Planned improvements:

- add Kafka streaming ingestion into the Bronze layer
- add Airflow DAG for orchestration
- add dbt models for transformation management
- add Great Expectations for advanced data validation
- add dashboard layer using Power BI, Superset, or Metabase
- add incremental loading and idempotency logic
- add dead-letter queue for invalid streaming events
- add structured logging and pipeline run metadata
- add Makefile for simplified commands

## Portfolio Summary

This project can be described as:

```text
Built a production-style Data Engineering pipeline using Python, Pandas, ClickHouse, Docker and SQL. Designed a medallion warehouse architecture with Bronze, Silver and Gold layers, implemented data cleaning and validation logic, created Data Quality reporting, added reusable analytics SQL queries, and covered transformation logic with automated unit tests and GitHub Actions CI.
```
