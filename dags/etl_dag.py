"""
Airflow DAG для нашего ETL pipeline.
"""

import sys
from datetime import datetime

sys.path.insert(0, "/opt/airflow/etl_project")

from airflow.decorators import dag, task


@dag(
    dag_id="etl_orders_pipeline",
    description="Extract -> Transform -> Load заказов в ClickHouse",
    schedule="@daily",
    start_date=datetime(2026, 7, 1),
    catchup=False,
    tags=["etl", "clickhouse", "learning"],
)
def etl_orders_pipeline():

    @task
    def extract_task():
        from pipeline_clickhouse import extract
        df = extract()
        return df.to_dict(orient="records")

    @task
    def transform_task(raw_records: list):
        import pandas as pd
        from pipeline_clickhouse import transform

        df = pd.DataFrame(raw_records)
        clean_df = transform(df)
        clean_df["order_date"] = clean_df["order_date"].astype(str)
        return clean_df.to_dict(orient="records")

    @task
    def load_task(clean_records: list):
        import pandas as pd
        from pipeline_clickhouse import load

        df = pd.DataFrame(clean_records)
        df["order_date"] = pd.to_datetime(df["order_date"]).dt.date
        load(df)

    raw = extract_task()
    clean = transform_task(raw)
    load_task(clean)


etl_orders_pipeline()