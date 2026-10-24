from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

BOOTSTRAP = "localhost:9092"
TOPIC = "accelerometer-data"

admin = KafkaAdminClient(bootstrap_servers=BOOTSTRAP, client_id="accelerometer-admin")

try:
    admin.create_topics([
        NewTopic(name=TOPIC, num_partitions=1, replication_factor=1)
    ])
    print("Topic created:", TOPIC)
except TopicAlreadyExistsError:
    print("Topic already exists:", TOPIC)
finally:
    admin.close()
