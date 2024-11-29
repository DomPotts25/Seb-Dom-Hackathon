import os
import matplotlib.pyplot as plt
import ximu3
import ximu3csv
from datetime import datetime

# Convert binary file
DESTINATION = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data")

NAME = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data", "2024-11-29_14-15-30.ximu3")

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
