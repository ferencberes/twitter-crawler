# Kafka resources

If you want to push the collected data to Kafka queues then you need to execute a few additional steps.

## Setup

**1.) Install Kafka**

```bash
conda activate YOUR_ENV
cd resources
./install_kafka.sh
```

**NOTE:** `conda` is used to install `openjdk`.

**2. Start Zookeeper and Kafka**

```bash
./zookeeper.sh start
./kafka.sh start
```

**3. Create a Kafka topic for your experiments**

In this example, we create a topic called `sample` and suppose that Kafka is using its default port 9092.

```bash
./topic.sh 9092 sample create
```
**NOTE:** This topic will be available every time we start Kafka. So there is no need to create it multiple times.

## Test

Before using `twittercrawler` with Kafka, you should test your environment.

**I.) Start producer**

```bash
conda activate YOUR_ENV
cd resources
./topic.sh 9092 sample producer
```

**II.) Start consumer in a different console**

```bash
conda activate YOUR_ENV
cd resources
./topic.sh 9092 sample consumer
```

**III.) Send messages**

Every message that you send from the producer console should arrive in the consumer console.

If your test was successful then you will be able to use the `KafkaWriter` and `KafkaReader` [objects](../twittercrawler/data_io.py) to process the collected tweets.

## Shutdown

Follow the steps below to shutdown your environment properly.

```bash
conda activate YOUR_ENV
cd resources
./kafka.sh stop
./zookeeper.sh stop
```