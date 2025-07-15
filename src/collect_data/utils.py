import pprint
from airsim import MultirotorClient

def print_state(client: MultirotorClient):
    state = client.getMultirotorState()
    print("State:\n", pprint.pformat(state))

def print_sensors(client: MultirotorClient):
    imu_data = client.getImuData()
    print("IMU:\n", pprint.pformat(imu_data))

    barometer_data = client.getBarometerData()
    print("Barometer:\n", pprint.pformat(barometer_data))

    magnetometer_data = client.getMagnetometerData()
    print("Magnetometer:\n", pprint.pformat(magnetometer_data))

    gps_data = client.getGpsData()
    print("GPS:\n", pprint.pformat(gps_data))
    