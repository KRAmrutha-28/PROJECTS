import requests
import json
import time
from kafka import KafkaProducer


PHONE_IP = "10.84.17.241"
PHONE_PORT = 8080

PHYPhOX_URL = f"http://{PHONE_IP}:{PHONE_PORT}"

KAFKA_SERVER = "localhost:9092"
TOPIC = "accelerometer"


producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda value:
        json.dumps(value).encode("utf-8")
)


def receive_accelerometer_data():

    url = (
        PHYPhOX_URL +
        "/get?accX&accY&accZ&acc_time"
    )

    response = requests.get(
        url,
        timeout=5
    )

    response.raise_for_status()

    return response.json()


def extract_data(data):

    buffer = data.get("buffer", {})

    acc_x = buffer.get("accX", {})
    acc_y = buffer.get("accY", {})
    acc_z = buffer.get("accZ", {})
    acc_time = buffer.get("acc_time", {})

    x_values = acc_x.get("buffer", [])
    y_values = acc_y.get("buffer", [])
    z_values = acc_z.get("buffer", [])
    time_values = acc_time.get("buffer", [])

    samples = []

    length = min(
        len(x_values),
        len(y_values),
        len(z_values),
        len(time_values)
    )

    for i in range(length):

        sample = {
            "timestamp": float(time_values[i]),
            "acc_x": float(x_values[i]),
            "acc_y": float(y_values[i]),
            "acc_z": float(z_values[i])
        }

        samples.append(sample)

    return samples


def publish_data():

    print("Starting Kafka producer...")
    print("Reading accelerometer data from:")
    print(PHYPhOX_URL)

    while True:

        try:

            data = receive_accelerometer_data()

            samples = extract_data(data)

            for sample in samples:

                producer.send(
                    TOPIC,
                    value=sample
                )

                print(
                    "SENT:",
                    sample
                )

            producer.flush()

            time.sleep(1)

        except Exception as e:

            print(
                "Producer error:",
                e
            )

            time.sleep(2)


if __name__ == "__main__":

    publish_data()