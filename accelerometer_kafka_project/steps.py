import csv
import math
import os
import sqlite3
from datetime import datetime

DB_FILE = os.path.join("data", "accelerometer.db")
OUT_CSV = os.path.join("data", "step_metrics.csv")

def parse_time(value):
    value = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None

def calculate():
    if not os.path.exists(DB_FILE):
        print("Database not found. Run the receiver -> producer -> consumer first.")
        return

    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute(
        "SELECT timestamp, x, y, z, magnitude FROM accelerometer_data ORDER BY id"
    ).fetchall()
    conn.close()

    if not rows:
        print("No accelerometer rows in the database.")
        return

    # Simple educational step detector:
    # use dynamic acceleration = |magnitude - gravity| and count upward
    # crossings above a threshold with a refractory period.
    threshold = 1.8
    min_step_gap = 0.28
    last_step_time = None
    steps = 0

    parsed = []
    for ts, x, y, z, magnitude in rows:
        dt = parse_time(ts)
        if dt is not None:
            parsed.append((dt, magnitude))

    previous_signal = None
    for dt, magnitude in parsed:
        signal = abs(magnitude - 9.80665)
        if previous_signal is not None:
            if previous_signal < threshold <= signal:
                if last_step_time is None or (dt - last_step_time).total_seconds() >= min_step_gap:
                    steps += 1
                    last_step_time = dt
        previous_signal = signal

    # Steps per minute based on elapsed data time.
    duration_seconds = 0
    if len(parsed) >= 2:
        duration_seconds = max(
            0, (parsed[-1][0] - parsed[0][0]).total_seconds()
        )

    minutes = max(duration_seconds / 60.0, 1 / 60.0)
    steps_per_minute = steps / minutes

    # Create one summary row; the full per-minute calculation below uses
    # the minute bucket of each detected step.
    minute_counts = {}
    last_step_time = None
    previous_signal = None

    for dt, magnitude in parsed:
        signal = abs(magnitude - 9.80665)
        if previous_signal is not None and previous_signal < threshold <= signal:
            if last_step_time is None or (dt - last_step_time).total_seconds() >= min_step_gap:
                key = dt.replace(second=0, microsecond=0).isoformat()
                minute_counts[key] = minute_counts.get(key, 0) + 1
                last_step_time = dt
        previous_signal = signal

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["minute", "steps"])
        for minute, count in sorted(minute_counts.items()):
            writer.writerow([minute, count])

    print("\nSTEP METRICS")
    print("-------------")
    print("Samples:", len(rows))
    print("Total steps:", steps)
    print("Duration (seconds):", round(duration_seconds, 2))
    print("Average steps/minute:", round(steps_per_minute, 2))
    print("Per-minute CSV:", OUT_CSV)
    print("\nNote: threshold-based step detection is an educational implementation.")
    print("For a research-grade result, calibrate threshold/windowing for the phone, orientation and sampling rate.")

if __name__ == "__main__":
    calculate()
