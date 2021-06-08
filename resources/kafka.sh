#!/bin/bash
action="$1"
cd kafka_2.11-1.1.0
if [ $action = "start" ]
then
bin/kafka-server-start.sh config/server.properties &
else
bin/kafka-server-stop.sh
fi
