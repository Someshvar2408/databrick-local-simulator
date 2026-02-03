CREATE TABLE IF NOT EXISTS default.orders_stream
(
    OrderID UInt32,
    CustomerID String,
    EmployeeID String,
    OrderDate Date,
    RequiredDate Date,
    ShippedDate Date,
    ShipVia UInt8,
    Freight Float64,
    ShipName String,
    ShipAddress String,
    ShipCity String,
    ShipRegion String,
    ShipPostalCode String,
    ShipCountry String,
    OrderDetailsRaw String,
    ingest_ts DateTime DEFAULT now()
)
ENGINE = MergeTree()
ORDER BY OrderID;

CREATE TABLE IF NOT EXISTS default.orders_kafka
(
    raw String
)
ENGINE = Kafka
SETTINGS
    kafka_broker_list = 'kafka:9092',
    kafka_topic_list = 'orders',
    kafka_group_name = 'clickhouse_orders_consumer',
    kafka_format = 'JSONAsString',
    kafka_num_consumers = 1,
    kafka_max_block_size = 1048576;

CREATE MATERIALIZED VIEW IF NOT EXISTS default.orders_stream_mv
TO default.orders_stream
AS
SELECT
    JSONExtractUInt(raw, 'OrderID') AS OrderID,
    JSONExtractString(raw, 'CustomerID') AS CustomerID,
    JSONExtractString(raw, 'EmployeeID') AS EmployeeID,
    toDate(JSONExtractString(raw, 'OrderDate')) AS OrderDate,
    toDate(JSONExtractString(raw, 'RequiredDate')) AS RequiredDate,
    toDate(JSONExtractString(raw, 'ShippedDate')) AS ShippedDate,
    toUInt8(JSONExtractUInt(raw, 'ShipVia')) AS ShipVia,
    toFloat64(JSONExtractFloat(raw, 'Freight')) AS Freight,
    JSONExtractString(raw, 'ShipName') AS ShipName,
    JSONExtractString(raw, 'ShipAddress') AS ShipAddress,
    JSONExtractString(raw, 'ShipCity') AS ShipCity,
    JSONExtractString(raw, 'ShipRegion') AS ShipRegion,
    JSONExtractString(raw, 'ShipPostalCode') AS ShipPostalCode,
    JSONExtractString(raw, 'ShipCountry') AS ShipCountry,
    JSONExtractRaw(raw, 'OrderDetails') AS OrderDetailsRaw,
    now() AS ingest_ts
FROM default.orders_kafka;
