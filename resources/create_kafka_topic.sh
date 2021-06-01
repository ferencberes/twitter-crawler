#!/bin/bash
bin/kafka-topics.sh --create --zookeeper localhost:$1 --replication-factor 1 --partitions 1 --topic $2
