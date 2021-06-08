#!/bin/bash
action="$1"
cd kafka_2.11-1.1.0
if [ $action = "start" ]
then
bin/zookeeper-server-start.sh config/zookeeper.properties &
else
bin/zookeeper-server-stop.sh
fi
