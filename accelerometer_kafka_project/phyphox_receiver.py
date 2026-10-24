import csv
import json
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

# Change this to the address shown by phyphox under "Allow remote access".
PHY_ADDRESS = "http://192.168.1.100:8080"
POLL_SECONDS = 0.25
CSV_FILE = os.path.join("data", "raw_accelerometer.csv")

os.makedirs("data", exist_ok=True)

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def ensure_csv():
    if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["timestamp", "x", "y", "z"])

def get_data(last_time=None):
    if last_time is None:
        params = ["acc_time=full", "accX=full", "accY=full", "accZ=full"]
    else:
        # Ask phyphox only for values after the latest time received.
        t = urllib.parse.quote(str(last_time), safe="")
        params = [
            "acc_time=" + t,
            "accX=" + t + "|acc_time",
            "accY=" + t + "|acc_time",
            "accZ=" + t + "|acc_time",
        ]

    url = PHY_ADDRESS.rstrip("/") + "/get?" + "&".join(params)
    with urllib.request.urlopen(url, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))

def extract_buffer(data, name):
    try:
        return data["buffer"][name]["buffer"]
    except (KeyError, TypeError):
        return []

def main():
    ensure_csv()
    print("[PHY] Reading from:", PHY_ADDRESS)
    print("[PHY] Start the Accelerometer experiment in phyphox before continuing.")
    print("[PHY] CSV:", CSV_FILE)

    last_time = None
    total = 0

    while True:
        try:
            data = get_data(last_time)
            times = extract_buffer(data, "acc_time")
            xs = extract_buffer(data, "accX")
            ys = extract_buffer(data, "accY")
            zs = extract_buffer(data, "accZ")

            n = min(len(times), len(xs), len(ys), len(zs))
            if n:
                with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    for i in range(n):
                        # phyphox acc_time is experiment-relative time.
                        # We preserve the current system time as the CSV timestamp.
                        writer.writerow([utc_now(), float(xs[i]), float(ys[i]), float(zs[i])])
                        total += 1
                last_time = times[n - 1]
                print(f"[PHY] received {n} samples; total={total}; last_acc_time={last_time}")
            time.sleep(POLL_SECONDS)

        except KeyboardInterrupt:
            print("\n[PHY] Stopped.")
            break
        except Exception as exc:
            print("[PHY] Connection/data error:", exc)
            print("[PHY] Check the phone IP, port, Wi-Fi and phyphox Remote Access.")
            time.sleep(2)

if __name__ == "__main__":
    main()
