Kafka in Docker
===

This repository provides everything you need to run Kafka in Docker.

Why?
---
The main hurdle of running Kafka in Docker is that it depends on Zookeeper.
Compared to other Kafka docker images, this one runs both Zookeeper and Kafka
in the same container. This means:

* No dependency on an external Zookeeper host, or linking to another container
* Zookeeper and Kafka are configured to work together out of the box

Run
---

```$ docker build --rm -t docker-kafka .
```

```$ docker run -it docker-kafka
```

Logs are stored in /tmp/kafka and /etc/kafka_manager.

KafkaManager
-----------------
This script runs on the Kafka host machine and provides a way so that other containers on the same network can access Kafka CLI tools for creating and modifying topics and brokers, and other Kafka housekeeping tasks. It runs on the host and continuously polls to respond to requests made to a special topic that all processes using Kafka can post to.

- Add/delete/list topics
- Add/remove(todo) brokers
- Scheduled infrastructure health check (todo)