import os
import matplotlib.pyplot as plt
import ximu3
import ximu3csv
from datetime import datetime

# Open connection
devices = ximu3.PortScanner.scan()

if not devices:
    raise Exception("No connections available")

print(f"Found {devices[0].device_name} {devices[0].serial_number}")

connection = ximu3.Connection(devices[0].connection_info)

if connection.open() != ximu3.RESULT_OK:
    raise Exception(f"Unable to open {devices[0].connection_info.to_string()}")

# Log data
DESTINATION = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data")

NAME = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

if ximu3.DataLogger.log(DESTINATION, NAME, [connection], 3) != ximu3.RESULT_OK:  # 3 seconds
    raise Exception("Data Logger failed")

connection.close()

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
