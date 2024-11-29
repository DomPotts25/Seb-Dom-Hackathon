import os
import ximu3
import ximu3csv
from datetime import datetime


def log_data(period: int, name: str = None):
    DESTINATION = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data")

    if name is None:
        # Open connection
        devices = ximu3.PortScanner.scan()

        if not devices:
            raise Exception("No connections available")

        print(f"Found {devices[0].device_name} {devices[0].serial_number}")

        connection = ximu3.Connection(devices[0].connection_info)

        if connection.open() != ximu3.RESULT_OK:
            raise Exception(f"Unable to open {devices[0].connection_info.to_string()}")

        # Log data
        NAME = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        if ximu3.DataLogger.log(DESTINATION, NAME, [connection], period) != ximu3.RESULT_OK:
            raise Exception("Data Logger failed")

        connection.close()
    else:
        NAME = name

    # Import data
    device = ximu3csv.read(os.path.join(DESTINATION, NAME))[0]

    # Return data
    seconds = device.inertial.timestamp / 1e6
    seconds -= seconds[0]

    return seconds, device.inertial.gyroscope.xyz, device.inertial.accelerometer.xyz
