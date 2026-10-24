import json
import math
import os
import sqlite3
from datetime import datetime, timezone

from kafka import KafkaConsumer

BOOTSTRAP = "localhost:9092"
TOPIC = "accelerometer-data"
DB_FILE = os.path.join("data", "accelerometer.db")

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def init_db(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS accelerometer_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            x REAL NOT NULL,
            y REAL NOT NULL,
            z REAL NOT NULL,
            magnitude REAL NOT NULL,
            received_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_accelerometer_timestamp
        ON accelerometer_data(timestamp)
    """)
    conn.commit()

def insert_data(conn, record):
    x = float(record["x"])
    y = float(record["y"])
    z = float(record["z"])
    magnitude = math.sqrt(x*x + y*y + z*z)

    conn.execute(
        """INSERT INTO accelerometer_data
           (timestamp, x, y, z, magnitude, received_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (record["timestamp"], x, y, z, magnitude, utc_now()),
    )
    conn.commit()

def run():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    init_db(conn)

    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=[BOOTSTRAP],
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="accelerometer-db-consumer",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )

    print("[CONSUMER] Connected to Kafka")
    print("[CONSUMER] Topic:", TOPIC)
    print("[CONSUMER] Database:", DB_FILE)

    for message in consumer:
        record = message.value
        try:
            insert_data(conn, record)
            print(
                f"[CONSUMER] Saved id={message.offset} "
                f"x={record['x']:.3f} y={record['y']:.3f} z={record['z']:.3f}"
            )
        except Exception as exc:
            print("[CONSUMER] Database error:", exc)

if __name__ == "__main__":
    run()
