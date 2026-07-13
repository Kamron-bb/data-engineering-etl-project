from pathlib import Path

import clickhouse_connect
import pandas as pd

from src.common.config import get_clickhouse_config


ANALYTICS_SQL_DIR = Path("sql/analytics")


def get_client():
    config = get_clickhouse_config()

    return clickhouse_connect.get_client(
        host=config.host,
        port=config.port,
        username=config.username,
        password=config.password,
        database=config.database,
    )


def run_query_file(client, file_path: Path) -> None:
    query = file_path.read_text().strip().rstrip(";")

    print("\n" + "=" * 80)
    print(f"Running query: {file_path.name}")
    print("=" * 80)

    result = client.query(query)

    if not result.result_rows:
        print("No results.")
        return

    df = pd.DataFrame(result.result_rows, columns=result.column_names)
    print(df.to_string(index=False))


def main() -> None:
    client = get_client()

    query_files = sorted(ANALYTICS_SQL_DIR.glob("*.sql"))

    if not query_files:
        print("No SQL files found in sql/analytics.")
        return

    for file_path in query_files:
        run_query_file(client, file_path)


if __name__ == "__main__":
    main()
