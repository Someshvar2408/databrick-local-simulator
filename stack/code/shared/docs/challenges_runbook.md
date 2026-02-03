# Northwind Challenges Runbook

This runbook maps each challenge in `Tasks.md` to the code artifacts and steps in this repo.

## Challenge 1: Real-Time Order Ingestion

**Artifacts**
- ClickHouse setup SQL: `stack/code/shared/etl/northwind/orders_stream_setup.sql`
- Airflow DAG: `stack/code/airflow/dags/northwind_orders_stream_ingestion_dag.py`

**Steps**
1. Start the stack: `sh env-up.sh`.
2. In Airflow, run the DAG `northwind_orders_stream_ingestion` to create Kafka ingestion tables and MV.
3. Validate in ClickHouse UI (Tabix or ClickHouse UI):
   ```sql
   SELECT count() FROM orders_stream;
   SELECT * FROM orders_stream ORDER BY ingest_ts DESC LIMIT 10;
   ```

**Notes**
- Orders are produced by `app-orders` in `stack/app.yaml` and sent to Kafka topic `orders`.
- The ClickHouse Kafka engine + materialized view handles ingestion and recovery.

## Challenge 2: Product Price Change Tracking

**Artifacts**
- ClickHouse tables: `stack/code/shared/etl/northwind/product_price_tables.sql`
- ETL script: `stack/code/shared/etl/northwind/price_change_capture.py`
- Airflow DAG: `stack/code/airflow/dags/northwind_price_change_tracking_dag.py`

**Steps**
1. Ensure `app-price-updates` is running (updates Postgres every 5 minutes).
2. Run the DAG `northwind_price_change_tracking` (runs every 5 minutes).
3. Explore in ClickHouse or Superset:
   ```sql
   SELECT * FROM product_price_history ORDER BY changed_at DESC LIMIT 50;
   ```

**Superset chart idea**
```sql
SELECT
  product_id,
  toStartOfHour(changed_at) AS hour,
  avg(new_price) AS avg_price
FROM product_price_history
GROUP BY product_id, hour
ORDER BY hour;
```

## Challenge 3: Historical Order Analytics

**Artifacts**
- Trino external tables: `stack/code/shared/etl/northwind/historical_orders_trino.sql`
- Notebook: `stack/code/notebook/challenge3_historical_orders.ipynb`

**Steps**
1. In Hue or Trino CLI, run `historical_orders_trino.sql` to register tables from S3 (LocalStack).
2. Use Superset SQL Lab to build charts for total sales, top products, and sales by country.

## Challenge 4: Real-Time Sales Dashboard

Use `orders_stream` as your dataset in Superset.

**Orders per minute (last 30 minutes)**
```sql
SELECT
  toStartOfMinute(ingest_ts) AS minute,
  count() AS orders
FROM orders_stream
WHERE ingest_ts >= now() - INTERVAL 30 MINUTE
GROUP BY minute
ORDER BY minute;
```

**Top 5 selling products (real-time)**
```sql
SELECT
  product_id,
  sum(quantity) AS units
FROM (
  SELECT
    arrayJoin(JSONExtractArrayRaw(OrderDetailsRaw)) AS detail,
    JSONExtractUInt(detail, 'ProductID') AS product_id,
    JSONExtractUInt(detail, 'Quantity') AS quantity
  FROM orders_stream
  WHERE ingest_ts >= now() - INTERVAL 30 MINUTE
)
GROUP BY product_id
ORDER BY units DESC
LIMIT 5;
```

**Average order value (real-time)**
```sql
SELECT avg(order_total) AS avg_order_value
FROM (
  SELECT
    OrderID,
    sum(
      JSONExtractFloat(detail, 'UnitPrice')
      * JSONExtractUInt(detail, 'Quantity')
      * (1 - JSONExtractFloat(detail, 'Discount'))
    ) AS order_total
  FROM (
    SELECT OrderID, arrayJoin(JSONExtractArrayRaw(OrderDetailsRaw)) AS detail
    FROM orders_stream
    WHERE ingest_ts >= now() - INTERVAL 30 MINUTE
  )
  GROUP BY OrderID
);
```

## Challenge 5: Data Quality & Monitoring

**Artifacts**
- Data quality checks: `stack/code/shared/etl/northwind/orders_quality_check.py`
- Airflow DAG: `stack/code/airflow/dags/northwind_orders_quality_dag.py`
- Notebook: `stack/code/notebook/challenge5_data_quality.ipynb`

**Steps**
1. Run DAG `northwind_orders_quality_checks` (every 10 minutes).
2. Failures are logged in Airflow and the task will error if checks fail.

## Challenge 6: Clickstream Analytics from User Flow Events

**Artifacts**
- Kafka sink config: `stack/code/trino/kafka-clickhouse-sink.json`
- ClickHouse table SQL: `stack/code/trino/clickhouse-table.txt`
- Notebook: `stack/code/notebook/challenge6_clickstream.ipynb`

**Steps**
1. Create `user_clickstream` table in ClickHouse (see SQL in notebook/readme).
2. Create the Kafka connector:
   ```sh
   curl -X POST -H "Content-Type: application/json" \
        --data @stack/code/trino/kafka-clickhouse-sink.json \
        http://localhost:8083/connectors
   ```
3. Use Superset to create datasets on `user_clickstream` and build charts.
