#!/bin/sh

# Start Zookeeper
/usr/share/zookeeper/bin/zkServer.sh start

# Wait until Zookeper starts
until /usr/share/zookeeper/bin/zkServer.sh status; do
    sleep 0.1
done

# Enable/disable auto creation of topics
if [ ! -z "$AUTO_CREATE_TOPICS" ]; then
    echo "auto.create.topics.enable: $AUTO_CREATE_TOPICS"
    echo "auto.create.topics.enable=$AUTO_CREATE_TOPICS" >> $KAFKA_HOME/config/server.properties
fi

# Run Kafka
$KAFKA_HOME/bin/kafka-server-start.sh $KAFKA_HOME/config/server.properties