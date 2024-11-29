import imufusion
import log_data
import matplotlib.pyplot as plt
import numpy as np
import scipy


def integrate(input, delta_time):
    output = np.zeros_like(input)

    for index, _ in enumerate(input):
        output[index] = output[index - 1] + delta_time[index] * input[index]

    return output


def hp_filter(input, bandwidth, sample_rate):
    b, a = scipy.signal.butter(1, bandwidth / (0.5 * sample_rate), btype="high")  # 1st order

    return scipy.signal.filtfilt(b, a, input, axis=0)


def lp_filter(input, bandwidth, sample_rate):
    b, a = scipy.signal.butter(1, bandwidth / (0.5 * sample_rate), btype="low")  # 1st order

    return scipy.signal.filtfilt(b, a, input, axis=0)


# Log data
timestamp, gyroscope, accelerometer = log_data.log_data(20, name="2024-11-29_15-59-46")

# # Plot data
# _, axes = plt.subplots(nrows=2, sharex=True)

# axes[0].plot(timestamp, gyroscope[:, 0], "tab:red", label="X")
# axes[0].plot(timestamp, gyroscope[:, 1], "tab:green", label="Y")
# axes[0].plot(timestamp, gyroscope[:, 2], "tab:blue", label="Z")
# axes[0].set_title("Gyroscope")
# axes[0].set_xlabel("Seconds")
# axes[0].set_ylabel("dps")
# axes[0].grid()
# axes[0].legend()

# axes[1].plot(timestamp, accelerometer[:, 0], "tab:red", label="X")
# axes[1].plot(timestamp, accelerometer[:, 1], "tab:green", label="Y")
# axes[1].plot(timestamp, accelerometer[:, 2], "tab:blue", label="Z")
# axes[1].set_title("Acelerometer")
# axes[1].set_xlabel("Seconds")
# axes[1].set_ylabel("g")
# axes[1].grid()
# axes[1].legend()

# Instantiate AHRS algorithms
SAMPLE_RATE = 2000  # 2000 Hz

offset = imufusion.Offset(SAMPLE_RATE)
ahrs = imufusion.Ahrs()

ahrs.settings = imufusion.Settings(
    imufusion.CONVENTION_NWU,
    0.5,  # gain
    2000,  # gyroscope range
    10,  # acceleration rejection
    0,  # magnetic rejection
    5 * SAMPLE_RATE,
)  # rejection timeout = 5 seconds

# Process sensor data
delta_time = np.diff(timestamp, prepend=timestamp[0])

acceleration = np.empty_like(accelerometer)

for index in range(len(timestamp)):
    gyroscope[index] = offset.update(gyroscope[index])

    ahrs.update_no_magnetometer(gyroscope[index], accelerometer[index], delta_time[index])

    acceleration[index] = 9.81 * ahrs.earth_acceleration  # convert g to m/s/s

# Plot acceleration
_, axes = plt.subplots(nrows=4, sharex=True, gridspec_kw={"height_ratios": [6, 1, 6, 6]})

axes[0].plot(timestamp, acceleration[:, 0], "tab:red", label="X")
axes[0].plot(timestamp, acceleration[:, 1], "tab:green", label="Y")
axes[0].plot(timestamp, acceleration[:, 2], "tab:blue", label="Z")
axes[0].set_title("Acceleration")
axes[0].set_ylabel("m/s/s")
axes[0].grid()
axes[0].legend()

# Plot velocity
velocity = integrate(acceleration, delta_time)

# velocity = hp_filter(velocity, 0.5, SAMPLE_RATE)

axes[2].plot(timestamp, velocity[:, 0], "tab:red", label="X")
axes[2].plot(timestamp, velocity[:, 1], "tab:green", label="Y")
axes[2].plot(timestamp, velocity[:, 2], "tab:blue", label="Z")
axes[2].set_title("Velocity")
axes[2].set_ylabel("m/s")
axes[2].grid()
axes[2].legend()

# Plot position
position = integrate(velocity, delta_time)

axes[3].plot(timestamp, position[:, 0], "tab:red", label="X")
axes[3].plot(timestamp, position[:, 1], "tab:green", label="Y")
axes[3].plot(timestamp, position[:, 2], "tab:blue", label="Z")
axes[3].set_title("Position")
axes[3].set_xlabel("Seconds")
axes[3].set_ylabel("m")
axes[3].grid()
axes[3].legend()

plt.show()
