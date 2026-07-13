from src.transformations.orders_transform import (
    build_gold_daily_revenue,
    calculate_data_quality,
    transform_orders,
)



from datetime import date
from pathlib import Path
import random

import clickhouse_connect
import pandas as pd

from src.common.config import get_clickhouse_config


SQL_FILE_PATH = Path("sql/ddl/clickhouse_tables.sql")


def get_client():
    config = get_clickhouse_config()

    return clickhouse_connect.get_client(
        host=config.host,
        port=config.port,
        username=config.username,
        password=config.password,
        database=config.database,
    )


def execute_sql_file(client) -> None:
    """
    Create ClickHouse database and tables.
    This executes SQL from sql/ddl/clickhouse_tables.sql.
    """
    sql_text = SQL_FILE_PATH.read_text()

    for statement in sql_text.split(";"):
        statement = statement.strip()
        if statement:
            client.command(statement)

    print("ClickHouse tables are ready.")


def extract_orders() -> pd.DataFrame:
    """
    Simulate raw order extraction from a source system.

    In a real project this source could be:
    - API
    - CRM
    - ERP
    - database replication
    - Kafka topic
    - SaaS platform
    """
    cities = ["London", "Berlin", "Paris", "Tashkent", None, ""]
    statuses = ["completed", "cancelled", "pending"]

    rows = []

    for order_id in range(1, 51):
        rows.append(
            {
                "order_id": order_id,
                "customer_id": random.randint(1000, 1050),
                "order_date": date(2026, random.randint(1, 3), random.randint(1, 28)),
                "city": random.choice(cities),
                "amount": random.choice(
                    [
                        round(random.uniform(20, 500), 2),
                        None,
                        -50.0,
                    ]
                ),
                "status": random.choice(statuses),
            }
        )

    # Add duplicated records intentionally to test data quality logic
    rows.append(rows[0].copy())
    rows.append(rows[1].copy())

    return pd.DataFrame(rows)






def load_dataframe(client, table_name: str, df: pd.DataFrame, columns: list[str]) -> None:
    if df.empty:
        print(f"No rows to insert into {table_name}.")
        return

    client.insert(
        table=table_name,
        data=df[columns].values.tolist(),
        column_names=columns,
    )

    print(f"Inserted {len(df)} rows into {table_name}.")


def main() -> None:
    client = get_client()

    execute_sql_file(client)

    raw_df = extract_orders()
    clean_df = transform_orders(raw_df)
    dq_df = calculate_data_quality(raw_df, clean_df)
    gold_df = build_gold_daily_revenue(clean_df)

    # Bronze layer keeps raw source data.
    bronze_df = raw_df.copy()
    bronze_df["city"] = bronze_df["city"].fillna("")
    load_dataframe(
        client,
        "etl_db.bronze_orders_raw",
        bronze_df,
        ["order_id", "customer_id", "order_date", "city", "amount", "status"],
    )

    # Silver layer keeps cleaned and standardized data.
    load_dataframe(
        client,
        "etl_db.silver_orders_clean",
        clean_df,
        [
            "order_id",
            "customer_id",
            "order_date",
            "city",
            "amount",
            "status",
            "amount_with_tax",
            "month",
        ],
    )

    # Gold layer keeps business-ready aggregates.
    load_dataframe(
        client,
        "etl_db.gold_daily_revenue",
        gold_df,
        [
            "order_date",
            "total_orders",
            "total_revenue",
            "avg_order_value",
        ],
    )

    # Data quality observability table.
    load_dataframe(
        client,
        "etl_db.dq_orders_report",
        dq_df,
        [
            "check_date",
            "total_raw_rows",
            "duplicate_order_ids",
            "null_amount_count",
            "negative_amount_count",
            "null_city_count",
            "accepted_rows",
            "rejected_rows",
            "data_quality_score",
        ],
    )

    print("Pipeline finished successfully.")


if __name__ == "__main__":
    main()
