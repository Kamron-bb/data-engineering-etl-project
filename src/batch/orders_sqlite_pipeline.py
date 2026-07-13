"""
Мини ETL pipeline: Extract -> Transform -> Load
Источник (Extract) симулирован (генерируем "сырые" данные как будто с API интернет-магазина).
В реальном проекте extract() просто заменяется на requests.get(...) к настоящему API.
"""

import logging
import random
import sqlite3
from datetime import datetime, timedelta

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
log = logging.getLogger("etl")

DB_PATH = "warehouse.db"


# ---------- EXTRACT ----------
def extract() -> pd.DataFrame:
    """
    Имитируем выгрузку заказов из внешнего источника (например, REST API магазина).
    В реальности здесь был бы: requests.get("https://api.shop.com/orders").json()
    """
    log.info("EXTRACT: тяну сырые данные из источника...")

    cities = ["Москва", "СПб", "Ташкент", "Алматы", "Новосибирск", None]  # None = грязные данные специально
    statuses = ["completed", "cancelled", "completed", "completed", "pending"]

    rows = []
    base_date = datetime(2026, 6, 1)
    for i in range(500):
        # специально добавляем "грязь" в данные, чтобы было что чистить на шаге Transform
        amount = round(random.uniform(-10, 500), 2)  # отрицательные суммы = мусор
        order_date = base_date + timedelta(days=random.randint(0, 40))
        rows.append({
            "order_id": i if random.random() > 0.02 else i - 1,  # немного дублей специально
            "city": random.choice(cities),
            "amount": amount if random.random() > 0.05 else None,  # немного пропусков
            "status": random.choice(statuses),
            "order_date": order_date.strftime("%Y-%m-%d"),
        })

    df = pd.DataFrame(rows)
    log.info(f"EXTRACT: получено {len(df)} сырых строк")
    return df


# ---------- TRANSFORM ----------
def transform(df: pd.DataFrame) -> pd.DataFrame:
    log.info("TRANSFORM: чищу и преобразую данные...")
    before = len(df)

    # 1. убираем дубликаты по order_id
    df = df.drop_duplicates(subset="order_id")

    # 2. выкидываем строки без суммы или с некорректной (отрицательной) суммой
    df = df.dropna(subset=["amount"])
    df = df[df["amount"] >= 0]

    # 3. выкидываем строки без города (не знаем, куда отнести заказ)
    df = df.dropna(subset=["city"])

    # 4. оставляем только завершённые заказы для аналитики выручки
    df = df[df["status"] == "completed"].copy()

    # 5. приводим типы
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["amount"] = df["amount"].round(2)

    # 6. добавляем производные поля
    df["amount_with_tax"] = (df["amount"] * 1.12).round(2)
    df["month"] = df["order_date"].dt.to_period("M").astype(str)

    after = len(df)
    log.info(f"TRANSFORM: было {before} строк -> стало {after} после очистки "
              f"(отсеяно {before - after} мусорных/дублирующихся)")
    return df


# ---------- LOAD ----------
def load(df: pd.DataFrame) -> None:
    log.info(f"LOAD: записываю {len(df)} чистых строк в {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    try:
        df.to_sql("orders_clean", conn, if_exists="replace", index=False)
        conn.commit()
        log.info("LOAD: успешно записано в таблицу orders_clean")
    except Exception as e:
        log.error(f"LOAD: ошибка записи — {e}")
        raise
    finally:
        conn.close()


# ---------- ORCHESTRATION ----------
def run_pipeline():
    log.info("=== Запуск pipeline ===")
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