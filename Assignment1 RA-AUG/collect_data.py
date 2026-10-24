import requests
import csv
import time
import os

# -----------------------------------------
# PHYphox connection
# -----------------------------------------
PHYphOX_URL = "http://192.0.0.4:8080"

# Recording duration
RECORDING_TIME = 300   # 300 seconds = 5 minutes

# CSV file
CSV_FILE = "accelerometer_data.csv"


# -----------------------------------------
# Function to send command to Phyphox
# -----------------------------------------
def control(command):
    url = PHYphOX_URL + "/control?cmd=" + command
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.json()


# -----------------------------------------
# Clear old experiment data
# -----------------------------------------
print("Clearing old Phyphox data...")

control("clear")

time.sleep(1)


# -----------------------------------------
# Start measurement
# -----------------------------------------
print("Starting Phyphox measurement...")

control("start")

time.sleep(1)

print("Recording started!")
print("Please walk normally for 5 minutes.")


# -----------------------------------------
# Create CSV file
# -----------------------------------------
with open(CSV_FILE, "w", newline="") as file:

    writer = csv.writer(file)

    # CSV header
    writer.writerow(["Time", "X", "Y", "Z"])

    start_time = time.time()

    last_phyphox_time = None

    total_rows = 0


    # -----------------------------------------
    # Collect data for 5 minutes
    # -----------------------------------------
    while time.time() - start_time < RECORDING_TIME:

        try:

            # First request: get complete current buffers
            if last_phyphox_time is None:

                url = (
                    PHYphOX_URL
                    + "/get?acc_time=full"
                    + "&accX=full"
                    + "&accY=full"
                    + "&accZ=full"
                )

            # Later requests: get only NEW data
            else:

                threshold = str(last_phyphox_time)

                url = (
                    PHYphOX_URL
                    + "/get?"
                    + "acc_time=" + threshold
                    + "&accX=" + threshold + "%7Cacc_time"
                    + "&accY=" + threshold + "%7Cacc_time"
                    + "&accZ=" + threshold + "%7Cacc_time"
                )

            response = requests.get(url, timeout=5)

            data = response.json()

            buffers = data["buffer"]

            times = buffers["acc_time"]["buffer"]
            x_values = buffers["accX"]["buffer"]
            y_values = buffers["accY"]["buffer"]
            z_values = buffers["accZ"]["buffer"]


            # -----------------------------------------
            # Save data
            # -----------------------------------------
            number_of_values = min(
                len(times),
                len(x_values),
                len(y_values),
                len(z_values)
            )

            for i in range(number_of_values):

                writer.writerow([
                    times[i],
                    x_values[i],
                    y_values[i],
                    z_values[i]
                ])

                total_rows += 1

            # Update latest time
            if len(times) > 0:
                last_phyphox_time = times[-1]


            # Show progress
            elapsed = time.time() - start_time

            print(
                f"Time: {elapsed:6.1f}s | "
                f"Data points: {total_rows}",
                end="\r"
            )


            # Small delay before next request
            time.sleep(0.2)


        except Exception as error:

            print("\nError:", error)

            time.sleep(1)


# -----------------------------------------
# Stop Phyphox
# -----------------------------------------
print("\n\nStopping Phyphox...")

control("stop")


# -----------------------------------------
# Finished
# -----------------------------------------
print("\nRecording completed!")
print("Total data points:", total_rows)
print("CSV file:", os.path.abspath(CSV_FILE))