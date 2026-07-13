"""
Kafka Consumer: непрерывно слушает поток заказов, батчами чистит и льёт в ClickHouse.
"""

import json

import pandas as pd
from kafka import KafkaConsumer

from pipeline_clickhouse import transform, get_client

TOPIC = "orders_stream"
BATCH_SIZE = 10


def ensure_stream_table(client):
    client.command("""
        CREATE TABLE IF NOT EXISTS orders_stream_clean (
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
    print("Таблица orders_stream_clean готова (движок MergeTree)")


def main():
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers="localhost:9092",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
        group_id="etl-consumer-group",
    )

    client = get_client()
    ensure_stream_table(client)

    batch = []
    print(f"Слушаю топик '{TOPIC}'... (Ctrl+C — остановить)\n")

    try:
        for message in consumer:
            batch.append(message.value)
            print(f"<- получен заказ #{message.value['order_id']} (в батче: {len(batch)}/{BATCH_SIZE})")

            if len(batch) >= BATCH_SIZE:
                df = pd.DataFrame(batch)
                clean_df = transform(df)

                if len(clean_df) > 0:
                    client.insert_df("orders_stream_clean", clean_df)
                    print(f"   записано {len(clean_df)} чистых строк в ClickHouse (из батча {len(batch)})\n")
                else:
                    print("   весь батч оказался мусором, нечего записывать\n")

                batch = []
    except KeyboardInterrupt:
        print("\nОстановлено пользователем")


if __name__ == "__main__":
    main()
