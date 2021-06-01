#!/bin/bash
conda install -c anaconda openjdk
wget https://archive.apache.org/dist/kafka/1.1.0/kafka_2.11-1.1.0.tgz
tar -xzf kafka_2.11-1.1.0.tgz
cd kafka_2.11-1.1.0
ls
