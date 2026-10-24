import csv
import json
import os
import time
from kafka import KafkaProducer
from kafka.errors import KafkaError

BOOTSTRAP = "localhost:9092"
TOPIC = "accelerometer-data"
CSV_FILE = os.path.join("data", "raw_accelerometer.csv")

def make_producer():
    return KafkaProducer(
        bootstrap_servers=[BOOTSTRAP],
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        acks="all",
        retries=5,
    )

def stream_new_rows():
    print("[PRODUCER] Connecting to Kafka:", BOOTSTRAP)
    producer = make_producer()
    print("[PRODUCER] Watching:", CSV_FILE)
    sent = 0

    while not os.path.exists(CSV_FILE):
        print("[PRODUCER] Waiting for receiver CSV...")
        time.sleep(1)

    # Skip header and start at end so old records are not resent.
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        next(f, None)
        f.seek(0, os.SEEK_END)

        while True:
            line = f.readline()
            if not line:
                time.sleep(0.2)
                continue

            try:
                row = next(csv.reader([line]))
                if len(row) != 4:
                    continue
                record = {
                    "timestamp": row[0],
                    "x": float(row[1]),
                    "y": float(row[2]),
                    "z": float(row[3]),
                }
                future = producer.send(TOPIC, record)
                metadata = future.get(timeout=10)
                sent += 1
                print(f"[PRODUCER] #{sent} -> topic={metadata.topic}, partition={metadata.partition}, offset={metadata.offset} {record}")
            except (ValueError, KafkaError, Exception) as exc:
                print("[PRODUCER] Error:", exc)
                time.sleep(2)

if __name__ == "__main__":
    stream_new_rows()
