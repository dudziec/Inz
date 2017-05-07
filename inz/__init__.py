from inz.view import *
from inz.bluetooth_server import BluetoothServer
from inz.coordinates import Coordinates
import sys
import threading
import numpy as np

calibration_coefficients = []


def video_capture_function():
    """

    :return:
    """

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    SelectTemplate(yacht_coordinates, buoy_coordinates, calibration_coefficients)
    app.exec_()


def run_server():
    """

    :return:
    """
    bluetooth_server = BluetoothServer(yacht_coordinates, buoy_coordinates)
    bluetooth_server.handle_data()

if __name__ == "__main__":

    # kryteria wykonania
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # przygotuj punkty obiektu, jak np (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((7 * 9, 3), np.float32)
    objp[:, :2] = np.mgrid[0:9, 0:7].T.reshape(-1, 2)

    # Tablice do przechowywania punktów obiektu i punktów obrazu ze wszystkich zdjęć.

    objpoints = []  # punkty 3d ze świata rzeczywistego
    imgpoints = []  # punkty 2d na płaszczyźnie obrazu

    images = ["coordination_images/image1.jpg", "coordination_images/image1.jpg", "coordination_images/image3.jpg"]

    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Znajdź wierzchołki szachownicy
        ret, corners = cv2.findChessboardCorners(gray, (9, 7), None)
        # Jeżeli znaleziono, dodaj punkty obiektu, punkty obrazu (po zwiększeniu przybliżenia)
        if ret:
            objpoints.append(objp)

            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)
            img = cv2.drawChessboardCorners(img, (9, 7), corners2, ret)

    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    img = cv2.imread('coordination_images/image1.jpg')

    h, w = img.shape[:2]

    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

    calibration_coefficients = [mtx, dist, newcameramtx, roi]

    yacht_coordinates = Coordinates()
    buoy_coordinates = Coordinates()

    bluetooth_server_thread = threading.Thread(target=run_server, name="Bluetooth serwer thread")

    video_capture_thread = threading.Thread(target=video_capture_function, name="Video capture thread")

    bluetooth_server_thread.start()
    video_capture_thread.start()
