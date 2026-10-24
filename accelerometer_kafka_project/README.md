# Android Accelerometer → Python → Kafka → Database

This project implements the assignment pipeline:

Android/Phyphox (or simulator)
        ↓
Python receiver (IP + TCP port 9000)
        ↓
Kafka producer
        ↓
Kafka topic: accelerometer-data
        ↓
Kafka consumer
        ↓
SQLite database
        ↓
CSV + step/minute metrics

## Project structure

- `receiver.py` - receives x,y,z accelerometer records over TCP and writes `data/raw_accelerometer.csv`
- `producer.py` - reads the CSV continuously and publishes records to Kafka
- `consumer.py` - consumes Kafka records and inserts them into SQLite
- `steps.py` - calculates step count and steps/minute from stored accelerometer data
- `simulate_phone.py` - generates realistic test accelerometer data if a phone is not available
- `view_db.py` - displays database rows and metrics
- `requirements.txt` - Python packages
- `data/` - raw CSV and SQLite database
- `kafka/` - optional Windows Kafka notes
- `run_receiver.bat`, etc. - optional launcher files

## Data format

TCP accepts either:

1. CSV line:
`timestamp,x,y,z`

2. JSON line:
`{"timestamp":"2026-09-19T11:00:00.000Z","x":0.12,"y":9.71,"z":0.45}`

If timestamp is omitted, the receiver creates one.

## Database

SQLite file:
`data/accelerometer.db`

Table:
`accelerometer_data`

Columns:
- id
- timestamp
- x
- y
- z
- magnitude
- received_at

The `steps.py` program calculates:
- total steps
- steps per minute
- number of one-minute windows

## Important

For an actual phone, the phone and Windows PC must be on the same Wi-Fi network. Windows Firewall may need to allow TCP port 9000.


## Actual phyphox phone mode

`phyphox_receiver.py` uses phyphox's built-in Remote Interface. phyphox exposes a REST API when Remote Access is enabled. The standard accelerometer buffers are commonly `accX`, `accY`, `accZ`, and `acc_time`, but buffer names depend on the selected experiment.

1. Put phone and PC on the same Wi-Fi.
2. Open phyphox and select an accelerometer experiment such as Acceleration with g (Raw Sensors).
3. Start the measurement.
4. In phyphox, enable **Allow remote access**.
5. Note the address shown, for example `http://192.168.1.100:8080`.
6. Open `phyphox_receiver.py` and change `PHY_ADDRESS`.
7. Run `python phyphox_receiver.py`.
8. Keep it running for 3–5 minutes.
9. Stop with Ctrl+C.

If your experiment uses different buffer names, inspect the active experiment configuration or the phyphox `/config` endpoint and replace `accX`, `accY`, `accZ`, and `acc_time` in the script.

The phyphox documentation describes the `/get` REST endpoint and remote access; the API supports retrieving full buffers or only new values after a threshold. See:
- https://phyphox.org/docs/remote-interface/
- https://phyphox.org/docs/remote-interface/api-reference/

## No phone mode

Run `receiver.py` and `simulate_phone.py`. This creates walking-like x/y/z data for a complete demonstration.
