import json
import logging

from clickhouse_http import execute_sql

logging.basicConfig(level=logging.INFO)


def _fetch_count(sql: str) -> int:
    response = execute_sql(sql)
    payload = json.loads(response)
    data = payload.get("data", [])
    if not data:
        return 0
    return int(list(data[0].values())[0])


def run_quality_checks() -> None:
    duplicate_sql = (
        "SELECT count() AS duplicate_orders FROM ("
        "SELECT OrderID, count() AS c FROM orders_stream "
        "GROUP BY OrderID HAVING c > 1"
        ") FORMAT JSON"
    )
    duplicates = _fetch_count(duplicate_sql)

    missing_sql = (
        "SELECT count() AS missing_required FROM orders_stream "
        "WHERE OrderID = 0 OR CustomerID = '' OR OrderDate = toDate('1970-01-01') "
        "FORMAT JSON"
    )
    missing_required = _fetch_count(missing_sql)

    if duplicates > 0 or missing_required > 0:
        logging.error(
            "Data quality check failed: duplicates=%s missing_required=%s",
            duplicates,
            missing_required,
        )
        raise ValueError(
            f"Data quality check failed: duplicates={duplicates} missing_required={missing_required}"
        )

    logging.info("Data quality checks passed.")


if __name__ == "__main__":
    run_quality_checks()
