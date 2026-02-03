CREATE SCHEMA IF NOT EXISTS hive.northwind
WITH (location = 's3a://demo-bucket/northwind/');

CREATE TABLE IF NOT EXISTS hive.northwind.orders (
    OrderID INTEGER,
    CustomerID VARCHAR,
    EmployeeID INTEGER,
    OrderDate DATE,
    RequiredDate DATE,
    ShippedDate DATE,
    ShipVia INTEGER,
    Freight DOUBLE,
    ShipName VARCHAR,
    ShipAddress VARCHAR,
    ShipCity VARCHAR,
    ShipRegion VARCHAR,
    ShipPostalCode VARCHAR,
    ShipCountry VARCHAR
)
WITH (
    format = 'PARQUET',
    external_location = 's3a://demo-bucket/northwind/orders.parquet'
);

CREATE TABLE IF NOT EXISTS hive.northwind.order_details (
    OrderID INTEGER,
    ProductID INTEGER,
    UnitPrice DOUBLE,
    Quantity INTEGER,
    Discount DOUBLE
)
WITH (
    format = 'PARQUET',
    external_location = 's3a://demo-bucket/northwind/order_details.parquet'
);

-- Sample analytics queries for Superset or SQL Lab:
-- Total sales
-- SELECT SUM(UnitPrice * Quantity * (1 - Discount)) AS total_sales FROM hive.northwind.order_details;

-- Top products by sales
-- SELECT ProductID, SUM(UnitPrice * Quantity * (1 - Discount)) AS sales
-- FROM hive.northwind.order_details
-- GROUP BY ProductID
-- ORDER BY sales DESC
-- LIMIT 10;

-- Sales by country
-- SELECT o.ShipCountry, SUM(d.UnitPrice * d.Quantity * (1 - d.Discount)) AS sales
-- FROM hive.northwind.orders o
-- JOIN hive.northwind.order_details d ON o.OrderID = d.OrderID
-- GROUP BY o.ShipCountry
-- ORDER BY sales DESC;
