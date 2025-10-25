
# Kafka Sink Connectors

### To stream Kafka topic directly to targets like S3, Clickhouse use the following sink connectors

#### S3 Sink

```
curl -X POST -H "Content-Type: application/json" \
     --data @stack/code/trino/kafka-s3-sink.json \
     http://localhost:8083/connectors
```

#### Clickhouse Sink

```
curl -X POST -H "Content-Type: application/json" \
     --data @stack/code/trino/kafka-clickhouse-sink.json \
     http://localhost:8083/connectors
```

##### To list the number of connectors configured

```
curl http://localhost:8083/connectors

# output
["clickstream-s3-sink","clickhouse-sink"]
```

##### To Delete Sink connector

```
curl -X DELETE http://localhost:8083/connectors/<connector-name>
# Example 
curl -X DELETE http://localhost:8083/connectors/clickhouse-sink
```

##### To View Connector status

```
curl http://localhost:8083/connectors/{connector-name}/status
```

#### To View Config

```
curl http://localhost:8083/connectors/{connector-name}/config
```
