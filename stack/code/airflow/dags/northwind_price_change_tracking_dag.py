from datetime import datetime, timedelta
import sys

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator

sys.path.append("/code/shared/etl/northwind")

from price_change_capture import main as capture_price_changes


default_args = {
    "owner": "data-engineer",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="northwind_price_change_tracking",
    default_args=default_args,
    description="Track product price changes into ClickHouse history tables.",
    schedule="*/5 * * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["northwind", "prices", "clickhouse"],
) as dag:
    start = EmptyOperator(task_id="start")

    capture = PythonOperator(
        task_id="capture_price_changes",
        python_callable=capture_price_changes,
    )

    end = EmptyOperator(task_id="end")

    start >> capture >> end
