CREATE TABLE IF NOT EXISTS default.product_price_history
(
    product_id UInt32,
    old_price Nullable(Float64),
    new_price Float64,
    changed_at DateTime
)
ENGINE = MergeTree()
ORDER BY (product_id, changed_at);

CREATE TABLE IF NOT EXISTS default.product_prices_latest
(
    product_id UInt32,
    price Float64,
    updated_at DateTime
)
ENGINE = MergeTree()
ORDER BY (product_id, updated_at);
