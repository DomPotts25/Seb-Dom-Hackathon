import numpy
import matplotlib.pyplot as pyplot
from scipy import signal

# Select file
file_name = "27EA-D880-39C4-E879_2019-10-22_10-51-21_565"

# Import data
inertial_csv_data = numpy.genfromtxt("Data\\"+ file_name + "\\triaxial.csv", delimiter=',')
time = inertial_csv_data[:, 0] / 1000000
time = time - time[0]
accelerometer = inertial_csv_data[:, [1, 2, 3]]
gyroscope = inertial_csv_data[:, [4, 5, 6]]

# Calculate mean sample frequency
sample_frequency = 1 / numpy.mean(numpy.diff(time))


def plot_data(data, title):
    pyplot.figure()

    # Plot signal
    pyplot.subplot(211)
    pyplot.title(title)
    pyplot.plot(time, data)
    pyplot.xlim(time[0], time[-1])
    pyplot.ylabel("Magnitude")

    # Plot spectogram
    pyplot.subplot(212)
    if False:
        NFFT = int(sample_frequency * 3)  # 3 second window
        noverlap = NFFT - 1  # maximum
        pyplot.specgram(data, NFFT=NFFT, Fs=sample_frequency, noverlap=noverlap)
    if True:
        NFFT = int(sample_frequency * 1)  # 1 second window
        noverlap = int(sample_frequency * 0.1)  # maximum
        f, t, Sxx = signal.spectrogram(data, sample_frequency, nfft=NFFT, noverlap=noverlap)
        pyplot.pcolormesh(t, f, Sxx)
    pyplot.ylim(time[0], 15)
    pyplot.xlabel("Time")
    pyplot.ylabel("Frequency (Hz)")


def magnitude(data):
    return numpy.sqrt(numpy.square(data[:, 0]) + numpy.square(data[:, 1]) + numpy.square(data[:, 2]))


# Plot data
plot_data(gyroscope[:, 0], "Gyroscope X (dps)")
plot_data(gyroscope[:, 1], "Gyroscope Y (dps)")
plot_data(gyroscope[:, 2], "Gyroscope Z (dps)")
plot_data(magnitude(gyroscope), "Gyroscope XYZ (dps)")
plot_data(accelerometer[:, 0], "Accelerometer X (g)")
plot_data(accelerometer[:, 1], "Accelerometer Y (g)")
plot_data(accelerometer[:, 2], "Accelerometer Z (g)")
plot_data(magnitude(accelerometer), "Accelerometer XYZ (g)")
pyplot.show()
