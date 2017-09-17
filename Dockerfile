# Kafka and Zookeeper

FROM java:openjdk-8-jre

ENV DEBIAN_FRONTEND noninteractive
ENV SCALA_VERSION 2.11
ENV KAFKA_VERSION 0.10.1.0
ENV KAFKA_HOME /opt/kafka_"$SCALA_VERSION"-"$KAFKA_VERSION"
ENV AUTO_CREATE_TOPICS true
ENV KAFKA_MANAGER_CONFIG_DIR /etc/docker-kafka/config
ENV KAFKA_MANAGER_HOME /opt/kafka_manager
ENV DELETE_TOPIC_ENABLE true

# Install Kafka, Zookeeper and other needed things
RUN apt-get update && \
    apt-get install -y zookeeper wget supervisor dnsutils less && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean && \
    wget -q http://apache.mirrors.spacedump.net/kafka/"$KAFKA_VERSION"/kafka_"$SCALA_VERSION"-"$KAFKA_VERSION".tgz -O /tmp/kafka_"$SCALA_VERSION"-"$KAFKA_VERSION".tgz && \
    tar xfz /tmp/kafka_"$SCALA_VERSION"-"$KAFKA_VERSION".tgz -C /opt && \
    rm /tmp/kafka_"$SCALA_VERSION"-"$KAFKA_VERSION".tgz

# Get pip, install python dependency
RUN apt-get update && \
    apt-get install -y python-pip python-dev

# Create configuration directory
RUN mkdir -p $KAFKA_MANAGER_CONFIG_DIR

# Copy config
COPY config $KAFKA_MANAGER_CONFIG_DIR

# Run pip install
RUN pip install -r $KAFKA_MANAGER_CONFIG_DIR/requirements.txt

# Supervisor config
ADD supervisor/kafka.conf \
    supervisor/zookeeper.conf\
    supervisor/kafka_manager.conf /etc/supervisor/conf.d/

# 2181 is zookeeper, 9092 is kafka
EXPOSE 2181 9092

# Add Kafka Manager directory
RUN mkdir -p $KAFKA_MANAGER_HOME

# Copy script
COPY python/KafkaManager.py $KAFKA_MANAGER_HOME

ADD scripts/simple-start-kafka.sh /usr/bin/start-kafka.sh

RUN chmod +x /usr/bin/start-kafka.sh

# Supervisord will run our services
CMD ["supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
