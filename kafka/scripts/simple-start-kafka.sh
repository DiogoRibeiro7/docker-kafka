#!/bin/sh

# Start Zookeeper
/usr/share/zookeeper/bin/zkServer.sh start

# Wait until Zookeper starts
until /usr/share/zookeeper/bin/zkServer.sh status; do
    sleep 0.1
done

# Run Kafka
$KAFKA_HOME/bin/kafka-server-start.sh $KAFKA_HOME/config/server.properties