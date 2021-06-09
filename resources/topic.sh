#!/bin/bash
port=$1
topic=$2
action=$3
host=localhost
cd kafka_2.11-1.1.0
if [ $action = "create" ]
then
bin/kafka-topics.sh --create --zookeeper localhost:$port --replication-factor 1 --partitions 1 --topic $topic
elif [ $action = "producer" ]
then
bin/kafka-console-producer.sh --topic $topic --broker-list $host:$port
#echo bin/kafka-console-producer.sh --topic $topic --bootstrap-server $host:$port
else
bin/kafka-console-consumer.sh --topic $topic --from-beginning --bootstrap-server $host:$port
fi

