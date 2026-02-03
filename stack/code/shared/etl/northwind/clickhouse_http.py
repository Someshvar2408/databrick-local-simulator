import json
import logging
import os
from typing import Iterable, List, Optional

import requests

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "clickhouse")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", "8123"))
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "default")
CLICKHOUSE_DATABASE = os.getenv("CLICKHOUSE_DATABASE", "default")


def _split_statements(sql: str) -> List[str]:
    statements = []
    for statement in sql.split(";"):
        cleaned = statement.strip()
        if cleaned:
            statements.append(cleaned)
    return statements


def _post(sql: str, database: Optional[str] = None) -> str:
    db = database or CLICKHOUSE_DATABASE
    url = f"http://{CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}/"
    params = {"database": db}
    response = requests.post(
        url,
        params=params,
        data=sql.encode("utf-8"),
        auth=(CLICKHOUSE_USER, CLICKHOUSE_PASSWORD),
        timeout=30,
    )
    response.raise_for_status()
    return response.text


def execute_sql(sql: str, database: Optional[str] = None) -> str:
    logging.info("Executing ClickHouse SQL")
    return _post(sql, database=database)


def execute_sql_statements(statements: Iterable[str], database: Optional[str] = None) -> None:
    for statement in statements:
        execute_sql(statement, database=database)


def execute_sql_file(path: str, database: Optional[str] = None) -> None:
    with open(path, "r", encoding="utf-8") as handle:
        sql = handle.read()
    statements = _split_statements(sql)
    execute_sql_statements(statements, database=database)


def insert_json_each_row(table: str, rows: List[dict], database: Optional[str] = None) -> None:
    if not rows:
        return
    lines = "\n".join(json.dumps(row, separators=(",", ":")) for row in rows)
    sql = f"INSERT INTO {table} FORMAT JSONEachRow\n{lines}"
    execute_sql(sql, database=database)
