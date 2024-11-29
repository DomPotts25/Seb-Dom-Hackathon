import helpers
import ximu3
import numpy as np
import matplotlib.pyplot as plt
import time
import scipy.signal as signal
from scipy.fft import fft, fftfreq

TIME_INTERVAL = 10  # seconds
CUTOFF_LOW = 5      # Low cutoff frequency (Hz)
CUTOFF_HIGH = 100   # High cutoff frequency (Hz)

def bandpass_filter(data, lowcut, highcut, fs, order=4):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = signal.butter(order, [low, high], btype='band')
    return signal.filtfilt(b, a, data)

def compute_displacement(acceleration, dt):
    # Remove any DC offset
    acceleration -= np.mean(acceleration)
    
    # Integrate to obtain velocity
    velocity = np.cumsum(acceleration) * dt
    velocity -= np.mean(velocity)  # Remove drift in velocity

    # Integrate again to obtain displacement
    displacement = np.cumsum(velocity) * dt
    return displacement


def analyze_vibration_signature(accel_data, gyro_data, fs):

    magnitude_accel = np.linalg.norm(accel_data, axis=1)

    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(np.linspace(0, TIME_INTERVAL, len(magnitude_accel)), magnitude_accel)
    plt.title("Magnitude of Accleration vs Time")
    plt.xlabel("Time [s]")
    plt.ylabel("Magnitude of Accleration")

    filtered_accel = np.zeros_like(accel_data)
    for i in range(3):  # Loop over X, Y, Z axes
        filtered_accel[:, i] = bandpass_filter(accel_data[:, i], CUTOFF_LOW, CUTOFF_HIGH, fs)

    magnitude_accel = np.linalg.norm(filtered_accel, axis=1)

     # Get the number of samples
    N = len(magnitude_accel)
    
    # Compute the time step
    dt = 1.0 / fs
    
    # Perform the FFT on the magnitude of the acceleration
    fft_vals = fft(magnitude_accel)
    
    # Calculate the frequencies associated with the FFT results
    fft_freqs = fftfreq(N, dt)
    
    # Get only the positive frequencies
    positive_freqs = fft_freqs[:N // 2]
    magnitude_spectrum = np.abs(fft_vals[:N // 2])
    
    # Plot the results
    plt.figure(figsize=(12, 6))
    
    # Plot the magnitude of the acceleration in time domain
    plt.subplot(2, 1, 1)
    plt.plot(np.arange(N) * dt, magnitude_accel)
    plt.title("Acceleration Magnitude vs Time")
    plt.xlabel("Time [s]")
    plt.ylabel("Acceleration Magnitude [m/s²]")

    # Plot the frequency spectrum
    plt.subplot(2, 1, 2)
    plt.plot(positive_freqs, magnitude_spectrum)
    plt.title("Frequency Spectrum of Acceleration Magnitude")
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("Amplitude")
    
    # Tight layout
    plt.tight_layout()
    plt.show()


# Callback to handle incoming HighGAccelerometer data
def high_g_accelerometer_callback(message):
    try:
        #print(f"Accel Data: {message.x}, {message.y}, {message.z}")
        highg_data.append(np.array([float(message.x), float(message.y), float(message.z)]))
    except Exception as e:
        print(f"Error in callback: {e}")


def inertial_callback(message):
    try:
        #print(f"Gyro Data: {message.gyroscope_x}, {message.gyroscope_y}, {message.gyroscope_z}")
        gyro_data.append(np.array([float(message.gyroscope_x), float(message.gyroscope_y), float(message.gyroscope_z)]))
    except Exception as e:
        print(f"Error in callback: {e}")


def upsample_gyro_data(gyro_data, accel_sample_rate, gyro_sample_rate):
    num_samples = len(gyro_data)
    time_original = np.linspace(0, num_samples / gyro_sample_rate, num_samples)
    time_resampled = np.linspace(0, num_samples / gyro_sample_rate, accel_sample_rate * (num_samples // gyro_sample_rate))
    
    upsampled_gyro_x = np.interp(time_resampled, time_original, gyro_data[:, 0])
    upsampled_gyro_y = np.interp(time_resampled, time_original, gyro_data[:, 1])
    upsampled_gyro_z = np.interp(time_resampled, time_original, gyro_data[:, 2])
    
    upsampled_gyro = np.stack((upsampled_gyro_x, upsampled_gyro_y, upsampled_gyro_z), axis=1)
    return upsampled_gyro

# Initialize data storage
highg_data = []
gyro_data = []

# Discover available devices - USB
devices = ximu3.PortScanner.scan_filter(ximu3.CONNECTION_TYPE_USB)

if not devices:
        raise Exception("No USB connections available")

print(f"Found {devices[0].device_name} {devices[0].serial_number}")
connection = ximu3.Connection(devices[0].connection_info)

# Register the HighGAccelerometer callback
connection.add_high_g_accelerometer_callback(high_g_accelerometer_callback)
connection.add_inertial_callback(inertial_callback)

# Open the connection
if connection.open() != ximu3.RESULT_OK:
    raise Exception(f"Unable to open connection to {messages[0].device_name}")

# Send commands to configure and start streaming HighGAccelerometer data
connection.send_commands(['{"strobe":null}'], 2, 500)  # Optional: strobe LED for debugging

# Collect data for 10 seconds
time.sleep(TIME_INTERVAL)

# Stop the connection
connection.close()

highg_data = np.array(highg_data)
gyro_data = np.array(gyro_data)

gyro_sample_rate = len(gyro_data) // TIME_INTERVAL  # 4006 samples / 10 seconds
accel_sample_rate = len(highg_data) // TIME_INTERVAL  # 31440 samples / 10 seconds

upsampled_gyro_data = upsample_gyro_data(gyro_data, accel_sample_rate, gyro_sample_rate)

print(f"accel_data shape: {highg_data.shape}, dtype: {highg_data.dtype}")

# Analyze vibration signature with the upsampled gyroscope data
analyze_vibration_signature(highg_data, upsampled_gyro_data, accel_sample_rate)

#analyze_vibration_signature(highg_data, gyro_data, len(highg_data))




#UDP
#messages = ximu3.NetworkAnnouncement().get_messages_after_short_delay()
# if not messages:
    # raise Exception("No devices found.")

# print(f"Found {messages[0].device_name} {messages[0].serial_number}")
#connection = ximu3.Connection(messages[0].to_udp_connection_info())
#connection.run(messages[0].to_udp_connection_info())









# plt.figure(figsize=(10, 6))
# plt.plot(highg_data[:, 0], label='HighG Accel X')
# plt.plot(highg_data[:, 1], label='HighG Accel Y')
# plt.plot(highg_data[:, 2], label='HighG Accel Z')
# plt.legend()
# plt.title("HighG Accelerometer Data")
# plt.xlabel("Sample")
# plt.ylabel("Acceleration (g)")
# plt.grid()
# plt.show()

# # Compute magnitude of acceleration
# magnitude = np.sqrt(np.sum(highg_data**2, axis=1))  # Magnitude across all axes


# N = len(magnitude)  # Number of samples
# T = 1 / 1000  # Sampling interval (assuming 1000 Hz)
# yf = fft(magnitude)
# xf = fftfreq(N, T)[:N//2]

# # Plot the frequency spectrum
# import matplotlib.pyplot as plt
# plt.figure(figsize=(10, 6))
# plt.plot(xf, 2.0/N * np.abs(yf[:N//2]))
# plt.title("Frequency Spectrum of Acceleration Magnitude")
# plt.xlabel("Frequency (Hz)")
# plt.ylabel("Amplitude")
# plt.grid()
# plt.show()