import os
import sqlite3

DB_FILE = os.path.join("data", "accelerometer.db")

def main():
    if not os.path.exists(DB_FILE):
        print("Database does not exist yet.")
        return

    conn = sqlite3.connect(DB_FILE)
    count = conn.execute("SELECT COUNT(*) FROM accelerometer_data").fetchone()[0]
    print("Total database rows:", count)
    print("\nLast 20 samples:")
    rows = conn.execute("""
        SELECT id, timestamp, x, y, z, magnitude
        FROM accelerometer_data
        ORDER BY id DESC LIMIT 20
    """).fetchall()

    for row in reversed(rows):
        print(row)

    conn.close()

if __name__ == "__main__":
    main()
