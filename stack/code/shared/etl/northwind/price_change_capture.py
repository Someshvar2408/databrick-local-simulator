import json
import logging
import os
from datetime import datetime, timezone

import psycopg2

from clickhouse_http import execute_sql, execute_sql_file, insert_json_each_row


POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "northwind")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

TABLES_SQL = "/code/shared/etl/northwind/product_price_tables.sql"

logging.basicConfig(level=logging.INFO)


def fetch_postgres_prices() -> dict:
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    )
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT "ProductID", "UnitPrice" FROM products')
            rows = cur.fetchall()
            return {int(row[0]): float(row[1]) for row in rows}
    finally:
        conn.close()


def fetch_latest_prices() -> dict:
    sql = (
        "SELECT product_id, argMax(price, updated_at) AS price "
        "FROM product_prices_latest GROUP BY product_id FORMAT JSON"
    )
    response = execute_sql(sql)
    payload = json.loads(response)
    latest = {}
    for row in payload.get("data", []):
        latest[int(row["product_id"])] = float(row["price"])
    return latest


def main() -> None:
    execute_sql_file(TABLES_SQL)

    current_prices = fetch_postgres_prices()
    latest_prices = fetch_latest_prices()

    changes = []
    latest_rows = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    for product_id, new_price in current_prices.items():
        old_price = latest_prices.get(product_id)
        if old_price is None or abs(new_price - old_price) > 1e-9:
            changes.append(
                {
                    "product_id": product_id,
                    "old_price": old_price,
                    "new_price": new_price,
                    "changed_at": now,
                }
            )
            latest_rows.append(
                {
                    "product_id": product_id,
                    "price": new_price,
                    "updated_at": now,
                }
            )

    if not changes:
        logging.info("No price changes detected.")
        return

    insert_json_each_row("product_price_history", changes)
    insert_json_each_row("product_prices_latest", latest_rows)
    logging.info("Logged %s price change(s).", len(changes))


if __name__ == "__main__":
    main()
