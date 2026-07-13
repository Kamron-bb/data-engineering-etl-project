"""
Kafka Producer: имитирует поток новых заказов, приходящих в реальном времени.
"""

import json
import random
import time
from datetime import datetime

from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

TOPIC = "orders_stream"

cities = ["Москва", "СПб", "Ташкент", "Алматы", "Новосибирск", None]
statuses = ["completed", "cancelled", "completed", "completed", "pending"]

order_id = 1

print(f"Начинаю отправку потока заказов в топик '{TOPIC}'... (Ctrl+C — остановить)")

try:
    while True:
        amount = round(random.uniform(-10, 500), 2)
        event = {
            "order_id": order_id,
            "city": random.choice(cities),
            "amount": amount if random.random() > 0.05 else None,
            "status": random.choice(statuses),
            "order_date": datetime.now().strftime("%Y-%m-%d"),
        }
        producer.send(TOPIC, value=event)
        print(f"-> отправлен заказ #{order_id}: {event}")
        order_id += 1
        time.sleep(random.uniform(0.5, 2))
except KeyboardInterrupt:
    print("\nОстановлено пользователем")
finally:
    producer.flush()
    producer.close()
