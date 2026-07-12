"""
ETL pipeline v2: Extract -> Transform -> Load в ClickHouse (вместо SQLite)
"""

import logging
import os
import random
from datetime import datetime, timedelta

import clickhouse_connect
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
log = logging.getLogger("etl")

CLICKHOUSE_HOST = os.environ.get("CLICKHOUSE_HOST", "localhost")
CLICKHOUSE_PORT = 8123
CLICKHOUSE_DB = "etl_db"
CLICKHOUSE_USER = "default"
CLICKHOUSE_PASSWORD = "clickhouse123"


def extract() -> pd.DataFrame:
    log.info("EXTRACT: тяну сырые данные из источника...")

    cities = ["Москва", "СПб", "Ташкент", "Алматы", "Новосибирск", None]
    statuses = ["completed", "cancelled", "completed", "completed", "pending"]

    rows = []
    base_date = datetime(2026, 6, 1)
    for i in range(500):
        amount = round(random.uniform(-10, 500), 2)
        order_date = base_date + timedelta(days=random.randint(0, 40))
        rows.append({
            "order_id": i if random.random() > 0.02 else i - 1,
            "city": random.choice(cities),
            "amount": amount if random.random() > 0.05 else None,
            "status": random.choice(statuses),
            "order_date": order_date.strftime("%Y-%m-%d"),
        })

    df = pd.DataFrame(rows)
    log.info(f"EXTRACT: получено {len(df)} сырых строк")
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    log.info("TRANSFORM: чищу и преобразую данные...")
    before = len(df)

    df = df.drop_duplicates(subset="order_id")
    df = df.dropna(subset=["amount"])
    df = df[df["amount"] >= 0]
    df = df.dropna(subset=["city"])
    df = df[df["status"] == "completed"].copy()

    df["order_date"] = pd.to_datetime(df["order_date"]).dt.date
    df["amount"] = df["amount"].round(2)
    df["amount_with_tax"] = (df["amount"] * 1.12).round(2)
    df["month"] = pd.to_datetime(df["order_date"]).dt.to_period("M").astype(str)
    df["order_id"] = df["order_id"].astype("int32")

    after = len(df)
    log.info(f"TRANSFORM: было {before} строк -> стало {after} после очистки "
              f"(отсеяно {before - after} мусорных/дублирующихся)")
    return df


def get_client():
    return clickhouse_connect.get_client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_PORT,
        database=CLICKHOUSE_DB,
        username=CLICKHOUSE_USER,
        password=CLICKHOUSE_PASSWORD,
    )


def ensure_table(client):
    client.command("""
        CREATE TABLE IF NOT EXISTS orders_clean (
            order_id Int32,
            city String,
            amount Float64,
            status String,
            order_date Date,
            amount_with_tax Float64,
            month String
        )
        ENGINE = MergeTree()
        ORDER BY (order_date, city)
        PARTITION BY month
    """)
    log.info("LOAD: таблица orders_clean готова (движок MergeTree, партиции по месяцу)")


def load(df: pd.DataFrame) -> None:
    log.info(f"LOAD: подключаюсь к ClickHouse ({CLICKHOUSE_HOST}:{CLICKHOUSE_PORT})...")
    try:
        client = get_client()
        ensure_table(client)
        client.command("TRUNCATE TABLE orders_clean")
        client.insert_df("orders_clean", df)
        log.info(f"LOAD: успешно записано {len(df)} строк в ClickHouse")
    except Exception as e:
        log.error(f"LOAD: ошибка записи в ClickHouse — {e}")
        raise


def run_pipeline():
    log.info("=== Запуск pipeline (ClickHouse) ===")
    try:
        raw = extract()
        clean = transform(raw)
        load(clean)
        log.info("=== Pipeline завершён успешно ===")
    except Exception as e:
        log.error(f"Pipeline упал с ошибкой: {e}")
        raise


if __name__ == "__main__":
    run_pipeline()