import csv
import json
import os
import socket
from datetime import datetime, timezone

HOST = "0.0.0.0"
PORT = 9000
CSV_FILE = os.path.join("data", "raw_accelerometer.csv")

os.makedirs("data", exist_ok=True)

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def ensure_csv():
    if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["timestamp", "x", "y", "z"])

def parse_line(line):
    line = line.strip()
    if not line:
        return None

    try:
        obj = json.loads(line)
        return (
            obj.get("timestamp") or utc_now(),
            float(obj["x"]),
            float(obj["y"]),
            float(obj["z"]),
        )
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        pass

    parts = [p.strip() for p in line.split(",")]
    if len(parts) == 4:
        try:
            timestamp = parts[0] or utc_now()
            return timestamp, float(parts[1]), float(parts[2]), float(parts[3])
        except ValueError:
            return None

    # Also accept only x,y,z
    if len(parts) == 3:
        try:
            return utc_now(), float(parts[0]), float(parts[1]), float(parts[2])
        except ValueError:
            return None

    return None

def receive_accelerometer_data(conn, address):
    print(f"[RECEIVER] Phone/client connected: {address}")
    buffer = b""
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            buffer += chunk
            while b"\n" in buffer:
                raw, buffer = buffer.split(b"\n", 1)
                line = raw.decode("utf-8", errors="ignore")
                record = parse_line(line)
                if record:
                    writer.writerow(record)
                    f.flush()
                    print(f"[RECEIVER] {record}")
                else:
                    print(f"[RECEIVER] Ignored invalid line: {line!r}")

    if buffer.strip():
        record = parse_line(buffer.decode("utf-8", errors="ignore"))
        if record:
            with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(record)
    print(f"[RECEIVER] Client disconnected: {address}")

def start_server():
    ensure_csv()
    print(f"[RECEIVER] Listening on {HOST}:{PORT}")
    print(f"[RECEIVER] CSV output: {CSV_FILE}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(5)
        while True:
            conn, address = server.accept()
            try:
                receive_accelerometer_data(conn, address)
            except Exception as exc:
                print("[RECEIVER] Error:", exc)
            finally:
                conn.close()

if __name__ == "__main__":
    start_server()
