# ETL Project — мини pipeline (Extract → Transform → Load)

Учебный проект: демонстрирует базовый ETL-pipeline на Python.
Генерирует "сырые" данные о заказах, чистит их через pandas и загружает в SQLite (`warehouse.db`).

## Структура проекта

```
etl_project/
├── pipeline.py       # основной код: extract, transform, load
├── warehouse.db       # результат работы pipeline (создаётся автоматически)
├── venv/               # виртуальное окружение с установленными библиотеками
└── README.md          # этот файл
```

## Как запустить (если venv уже создан)

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

## Как посмотреть результат в базе данных

```bash
python3 -c "
import sqlite3
import pandas as pd

conn = sqlite3.connect('warehouse.db')
print(pd.read_sql('SELECT * FROM orders_clean LIMIT 5', conn).to_string())

query = '''
SELECT city, COUNT(*) as orders_count, ROUND(SUM(amount), 2) as total_revenue
FROM orders_clean
GROUP BY city
ORDER BY total_revenue DESC
'''
print(pd.read_sql(query, conn).to_string())
conn.close()
"
```

Или установить расширение **SQLite Viewer** в VS Code и открыть `warehouse.db` визуально, без кода.

## Запуск через VS Code

1. File → Open Folder → выбрать папку `etl_project`
2. Открыть `pipeline.py`
3. Проверить интерпретатор внизу справа в статус-баре — должен быть путь с `venv`
   (если не тот — Cmd+Shift+P → "Python: Select Interpreter" → выбрать интерпретатор
   с путём `./venv/bin/python`, либо вписать вручную путь
   `/Users/<ваше_имя>/etl_project/venv/bin/python3` через "Enter interpreter path...")
4. Нажать ▶️ "Run Python File" (или Cmd+F5)

## Частые ошибки и решения

| Ошибка | Причина | Решение |
|---|---|---|
| `ModuleNotFoundError: No module named 'pandas'` | Скрипт запускается не через venv | Активировать venv (`source venv/bin/activate`) перед запуском, либо переключить интерпретатор в VS Code |
| `sqlite3.OperationalError: unable to open database file` | Вы находитесь не в папке проекта (например, в `/`) | Проверить текущую папку командой `pwd`, вернуться командой `cd ~/etl_project` |
| В списке интерпретаторов VS Code нет venv | VS Code не просканировал папку | Использовать "Enter interpreter path..." и вписать путь вручную |

## Версия 2: pipeline_clickhouse.py (настоящая база вместо SQLite)

Та же логика Extract/Transform, но Load теперь пишет в **ClickHouse**, поднятый
локально через Docker — как в реальной работе data engineer.

### Файлы этой версии

```
etl_project/
├── docker-compose.yml       # описание контейнера ClickHouse
├── pipeline_clickhouse.py   # pipeline, пишущий в ClickHouse вместо SQLite
```

### Как запустить с нуля

```bash
cd ~/etl_project

# 1. Убедиться, что Docker Desktop запущен (иконка кита в верхнем меню macOS)
docker info

# 2. Поднять ClickHouse в контейнере
docker compose up -d

# 3. Проверить, что контейнер работает
docker ps
# должна быть строка etl_clickhouse со статусом Up

# 4. Активировать venv и поставить клиент для ClickHouse
source venv/bin/activate
pip install clickhouse-connect

# 5. Запустить pipeline
python3 pipeline_clickhouse.py
```

### Как остановить / полностью пересоздать ClickHouse

```bash
# Просто остановить (данные сохранятся)
docker compose stop

# Запустить снова после остановки
docker compose start

# Полностью удалить контейнер + данные (например, если поменяли пароль/схему)
docker compose down -v
docker compose up -d
```

### Как посмотреть данные в ClickHouse напрямую (без Python)

```bash
docker exec -it etl_clickhouse clickhouse-client --password clickhouse123

-- дальше внутри clickhouse-client:
SELECT city, count(*), round(sum(amount), 2) AS revenue
FROM etl_db.orders_clean
GROUP BY city
ORDER BY revenue DESC;
```//
Выход из clickhouse-client: команда `exit` или Ctrl+D.

### Данные подключения

| Параметр | Значение |
|---|---|
| Host | localhost |
| HTTP порт | 8123 |
| Нативный порт | 9000 |
| База | etl_db |
| Пользователь | default |
| Пароль | clickhouse123 |

### Частые ошибки (ClickHouse-версия)

| Ошибка | Причина | Решение |
|---|---|---|
| `unable to get image ... docker.sock: no such file or directory` | Docker Desktop не запущен | Открыть Docker.app, дождаться "Docker Desktop is running" |
| `no configuration file provided: not found` | `docker-compose.yml` не в текущей папке | `cd ~/etl_project`, проверить `ls` |
| `REQUIRED_PASSWORD` при подключении | Пароль пустой или не совпадает между `docker-compose.yml` и `pipeline_clickhouse.py` | Указать одинаковый пароль в обоих файлах, пересоздать контейнер (`docker compose down -v && docker compose up -d`) |
| `ModuleNotFoundError: No module named 'clickhouse_connect'` | Библиотека не установлена в активный venv | `source venv/bin/activate && pip install clickhouse-connect` |

## Версия 3: Airflow — автозапуск по расписанию

Тот же pipeline (extract/transform/load), но теперь запускается не вручную,
а автоматически, по расписанию, через Airflow — с историей запусков,
retry при ошибках и веб-интерфейсом для мониторинга.

### Новые файлы

```
etl_project/
├── dags/
│   └── etl_dag.py      # описание графа задач (DAG) для Airflow
```

`docker-compose.yml` и `pipeline_clickhouse.py` уже обновлены для поддержки Airflow
(добавлен сервис airflow, добавлена возможность задать CLICKHOUSE_HOST через переменную окружения).

### Как запустить

```bash
cd ~/etl_project

# пересоздаём контейнеры с учётом нового сервиса airflow
docker compose down -v
docker compose up -d

# первый запуск займёт 2-5 минут — Airflow инициализирует свою базу
# и ставит pandas/clickhouse-connect внутри контейнера
docker logs -f etl_airflow
```

Дождитесь в логах строки вида `Airflow is ready` и информации о логине/пароле
администратора (Airflow сам генерирует пароль при первом запуске в режиме `standalone`
и печатает его в лог — ищите строки со словом `password`).

### Открыть веб-интерфейс

Откройте в браузере: **http://localhost:8080**

Логин: `admin`, пароль — тот, что нашли в логах контейнера (команда выше).

### Что делать в интерфейсе

1. На главной странице (DAGs) найдите `etl_orders_pipeline`
2. Включите его переключателем слева (по умолчанию новые DAG выключены)
3. Нажмите на название DAG → кнопка ▶️ (Trigger DAG) справа сверху — запустит pipeline вручную,
   не дожидаясь расписания
4. Вкладка **Graph** — визуально покажет 3 задачи (extract → transform → load) и их статус
   (зелёный = успех, красный = ошибка)
5. Кликните на любую задачу → **Logs** — увидите те же логи, что раньше видели в терминале

### Частые ошибки (Airflow-версия)

| Ошибка | Причина | Решение |
|---|---|---|
| DAG не появляется в списке | Синтаксическая ошибка в `etl_dag.py`, или Airflow ещё не просканировал папку | Проверить `docker logs etl_airflow`, подождать ~30 сек, обновить страницу |
| `ModuleNotFoundError: No module named 'pipeline_clickhouse'` | Volume с кодом не примонтирован или путь неверный | Проверить, что в `docker-compose.yml` есть `- .:/opt/airflow/etl_project` |
| Задача `load_task` падает с ошибкой подключения | ClickHouse ещё не поднялся, когда Airflow пытается подключиться | Подождать, пока оба контейнера полностью запустятся (`docker ps`, статус `Up` у обоих) |
| Не могу найти пароль admin в логах | Слишком много строк в логах | `docker logs etl_airflow 2>&1 \| grep -i password` |

## Что дальше (идеи для развития проекта)

- dbt — перенести логику transform() из pandas в SQL-модели, запускаемые тем же Airflow
- Data quality проверки — добавить явные assert'ы с алертами вместо тихого отбрасывания строк
- Kafka — попробовать потоковую (а не батч) обработку данных
- Инициализировать git-репозиторий и залить на GitHub для портфолио
