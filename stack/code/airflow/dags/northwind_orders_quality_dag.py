from datetime import datetime, timedelta
import sys

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator

sys.path.append("/code/shared/etl/northwind")

from orders_quality_check import run_quality_checks


default_args = {
    "owner": "data-engineer",
    "depends_on_past": False,
    "retries": 0,
}

with DAG(
    dag_id="northwind_orders_quality_checks",
    default_args=default_args,
    description="Validate orders_stream for duplicates and required fields.",
    schedule="*/10 * * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["northwind", "data-quality"],
) as dag:
    start = EmptyOperator(task_id="start")

    check = PythonOperator(
        task_id="orders_quality_check",
        python_callable=run_quality_checks,
    )

    end = EmptyOperator(task_id="end")

    start >> check >> end
