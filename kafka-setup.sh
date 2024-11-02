bin/zookeeper-server-start.sh config/zookeeper.properties
bin/kafka-server-start.sh config/server.properties

# bin/kafka-topics.sh --bootstrap-server localhost:9092 --topic main-topic --create --partitions 3 --replication-factor 1
bin/kafka-topics.sh --bootstrap-server localhost:9092 --topic order-topic --create --partitions 1 --replication-factor 1

# Consume topic
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic main-topic --from-beginning
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic order-topic --from-beginning
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic payment-topic --from-beginning
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic shipping-topic --from-beginning

# List topics
bin/kafka-topics.sh --bootstrap-server localhost:9092 --list

# Clear topic
bin/kafka-topics.sh --bootstrap-server localhost:9092 --topic main-topic --delete
bin/kafka-topics.sh --bootstrap-server localhost:9092 --topic order-topic --delete
bin/kafka-topics.sh --bootstrap-server localhost:9092 --topic payment-topic --delete
bin/kafka-topics.sh --bootstrap-server localhost:9092 --topic shipping-topic --delete