from datetime import datetime, timedelta
import os
import sys

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

sys.path.append("/code/shared/etl/northwind")

import json

from clickhouse_http import execute_sql_file, execute_sql


def setup_orders_stream():
    sql_path = "/code/shared/etl/northwind/orders_stream_setup.sql"
    execute_sql_file(sql_path)


def validate_orders_stream():
    sql = (
        "SELECT count() AS recent_orders FROM orders_stream "
        "WHERE ingest_ts >= now() - INTERVAL 10 MINUTE FORMAT JSON"
    )
    response = execute_sql(sql)
    payload = json.loads(response)
    rows = payload.get("data", [])
    recent_orders = int(rows[0]["recent_orders"]) if rows else 0
    if recent_orders == 0:
        raise ValueError("No recent orders found in orders_stream.")


default_args = {
    "owner": "data-engineer",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="northwind_orders_stream_ingestion",
    default_args=default_args,
    description="Setup ClickHouse Kafka ingestion for orders_stream.",
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["northwind", "kafka", "clickhouse"],
) as dag:
    start = EmptyOperator(task_id="start")

    setup = PythonOperator(
        task_id="setup_orders_stream",
        python_callable=setup_orders_stream,
    )

    validate = PythonOperator(
        task_id="validate_orders_stream",
        python_callable=validate_orders_stream,
    )

    end = EmptyOperator(task_id="end")

    start >> setup >> validate >> end
