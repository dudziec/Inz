from inz.view import *
from inz.bluetooth_server import BluetoothServer
from inz.coordinates import Coordinates
import time
import sys
import threading


def video_capture_function():
    """

    :return:
    """

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    SelectTemplate(yacht_coordinates, buoy_coordinates)
    app.exec_()


def run_server():
    """

    :return:
    """
    bluetooth_server = BluetoothServer(yacht_coordinates, buoy_coordinates)
    bluetooth_server.handle_data()

if __name__ == "__main__":
    yacht_coordinates = Coordinates()
    buoy_coordinates = Coordinates()

    bluetooth_server_thread = threading.Thread(target=run_server, name="Bluetooth serwer thread")

    video_capture_thread = threading.Thread(target=video_capture_function, name="Video capture thread")

    bluetooth_server_thread.start()
    video_capture_thread.start()
