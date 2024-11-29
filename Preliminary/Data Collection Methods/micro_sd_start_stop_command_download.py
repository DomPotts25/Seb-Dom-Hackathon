import os
import matplotlib.pyplot as plt
import requests
import time
import ximu3
import ximu3csv
from datetime import datetime

# Open connection
messages = ximu3.NetworkAnnouncement().get_messages_after_short_delay()

if not messages:
    raise Exception("No connections available")

print(f"Found {messages[0].device_name} {messages[0].serial_number}")

connection = ximu3.Connection(messages[0].to_tcp_connection_info())

if connection.open() != ximu3.RESULT_OK:
    raise Exception(f"Unable to open {messages[0].to_tcp_connection_info().to_string()}")

connection.send_commands(['{"tcp_data_messages_enabled":false}'], 2, 500)  # disable data messages for TCP

# Log data
NAME = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

connection.send_commands([f'{{"start":"{NAME}"}}'], 2, 500)

time.sleep(3)

connection.send_commands(['{"stop":null}'], 2, 500)

# Download data
DESTINATION = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data")

FILE_NAME = NAME + ".ximu3"

FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data", FILE_NAME)

URL = f"http://{messages[0].ip_address}/{FILE_NAME}"

try:
    with open(FILE_PATH, "wb") as file:
        file.write(requests.get(URL).content)
except Exception as _:
    print(f"Unable to download {URL}")

# Convert binary file
ximu3.FileConverter.convert(DESTINATION, NAME, [FILE_PATH])

# Import data
device = ximu3csv.read(os.path.join(DESTINATION, NAME))[0]

# Plot data
_, axes = plt.subplots(nrows=2, sharex=True)

seconds = device.inertial.timestamp / 1e6
seconds -= seconds[0]

axes[0].plot(seconds, device.inertial.gyroscope.x, "tab:red", label="X")
axes[0].plot(seconds, device.inertial.gyroscope.y, "tab:green", label="Y")
axes[0].plot(seconds, device.inertial.gyroscope.z, "tab:blue", label="Z")
axes[0].set_title("Gyroscope")
axes[0].set_xlabel("Seconds")
axes[0].set_ylabel("dps")
axes[0].grid()
axes[0].legend()

axes[1].plot(seconds, device.inertial.accelerometer.x, "tab:red", label="X")
axes[1].plot(seconds, device.inertial.accelerometer.y, "tab:green", label="Y")
axes[1].plot(seconds, device.inertial.accelerometer.z, "tab:blue", label="Z")
axes[1].set_title("Acelerometer")
axes[1].set_xlabel("Seconds")
axes[1].set_ylabel("g")
axes[1].grid()
axes[1].legend()

plt.show()
