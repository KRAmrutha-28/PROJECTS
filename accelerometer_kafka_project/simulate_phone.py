import math
import random
import socket
import time
from datetime import datetime, timezone

HOST = "127.0.0.1"
PORT = 9000
SECONDS = 180
SAMPLE_RATE = 20

def iso_now():
    return datetime.now(timezone.utc).isoformat()

def run():
    print(f"[SIMULATOR] Sending {SECONDS}s of test accelerometer data to {HOST}:{PORT}")
    with socket.create_connection((HOST, PORT), timeout=10) as sock:
        total = SECONDS * SAMPLE_RATE
        for i in range(total):
            t = i / SAMPLE_RATE

            # Gravity plus a walking-like periodic component.
            walking = 2.3 * max(0.0, math.sin(2 * math.pi * 1.8 * t))
            x = 0.35 * math.sin(2 * math.pi * 1.8 * t) + random.gauss(0, 0.12)
            y = 9.80665 + walking + random.gauss(0, 0.18)
            z = 0.35 * math.cos(2 * math.pi * 1.8 * t) + random.gauss(0, 0.12)

            line = f"{iso_now()},{x:.4f},{y:.4f},{z:.4f}\n"
            sock.sendall(line.encode("utf-8"))
            time.sleep(1 / SAMPLE_RATE)

    print("[SIMULATOR] Finished.")

if __name__ == "__main__":
    run()
