# ETL Project — мини pipeline (Extract → Transform → Load)

Учебный проект: демонстрирует базовый ETL-pipeline на Python.
Генерирует "сырые" данные о заказах, чистит их через pandas и загружает в SQLite (`warehouse.db`).

## Структура проекта## Как запустить (если venv уже создан)

Открыть терминал (iTerm) и выполнить три команды:

```bash
cd ~/etl_project
source venv/bin/activate
python3 pipeline.py
```

Проверка: перед именем пользователя в терминале должно появиться `(venv)` — значит окружение активно.

## Как запустить с нуля (если venv ещё не создан или удалён)

```bash
cd ~/etl_project
python3 -m venv venv
source venv/bin/activate
pip install pandas
python3 pipeline.py
```

## Версия 2: pipeline_clickhouse.py (настоящая база вместо SQLite)

Та же логика Extract/Transform, но Load теперь пишет в ClickHouse, поднятый
локально через Docker — как в реальной работе data engineer.

### Как запустить с нуля

```bash
cd ~/etl_project
docker info
docker compose up -d
docker ps
source venv/bin/activate
pip install clickhouse-connect
python3 pipeline_clickhouse.py
```

### Данные подключения

| Параметр | Значение |
|---|---|
| Host | localhost |
| HTTP порт | 8123 |
| База | etl_db |
| Пользователь | default |
| Пароль | clickhouse123 |

## Версия 3: Airflow — автозапуск по расписанию

Тот же pipeline, но запускается автоматически по расписанию через Airflow.

### Как запустить

```bash
cd ~/etl_project
docker compose down -v
docker compose up -d
docker logs -f etl_airflow
```

Открыть веб-интерфейс: http://localhost:8080 (логин admin, пароль создаётся вручную командой airflow users create)

## Что дальше (идеи для развития проекта)

- dbt — перенести логику transform() из pandas в SQL-модели
- Data quality проверки
- Kafka — потоковая обработка данных
- Git/GitHub — готово ✅
