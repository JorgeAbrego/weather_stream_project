echo "Waiting for Kafka to come online..."

cub kafka-ready -b broker:29092 1 20

# create the topic
kafka-topics \
  --bootstrap-server broker:29092 \
  --topic jp-weather \
  --replication-factor 1 \
  --partitions 1 \
  --create

#sleep infinity