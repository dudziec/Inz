from inz.frame import *
from inz.view import *
import math

CAMERA_ANGLE = 78
MAST_HEIGHT = 0.3

class Video:
    def __init__(self, mode, op, yacht_coordinates, buoy_coordinates, calibration_coefficients):
        self.vc = cv2.VideoCapture(mode)
        # dla Logitech C920 FULL HD 1080p
        self.vc.set(3, 1920)
        self.vc.set(4, 1080)

        self.buoy = Buoy()
        self.yacht_coordinates = yacht_coordinates
        self.buoy_coordinates = buoy_coordinates
        self.operations = op
        self.mtx, self.dist, self.newcameramtx, self.roi = calibration_coefficients

    def capture(self, frame, template=None):
        i = 0
        while True:
            (grabbed, fr) = self.vc.read()

            fr = cv2.undistort(fr, self.mtx, self.dist, None, self.newcameramtx)
            x, y, w, h = self.roi
            fr = fr[y:y + h, x:x + w]

            i += 1

            if i % 6 == 0:
                continue

            if not grabbed:
                print("Video not found!")
                break

            h, w = fr.shape[:-1]

            frame.image = fr
            frame.mask = None
            frame.hsv = frame.to_hsv()
            frame.blur()
            frame.in_range(template.ranges)

            for o in self.operations:
                o()

            x, y = self.buoy.detect(frame, True)

            distance = self.buoy.compute_distance(template)

            distance = self.calculate_distance(MAST_HEIGHT, distance)

            x = int(self.buoy.center[0])

            cv2.line(frame.image, (x, 0), (x, h), (0, 255, 0), 2)
            cv2.line(frame.image, (int(w/2), 0), (int(w/2), h), (0, 255, 255), 1)

            angle = self.calculate_angle(CAMERA_ANGLE, x, w)

            cv2.putText(frame.image, "Dystans: " + str(distance)[0:6] + "m", (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, 255)
            cv2.putText(frame.image, "Korekta a1zymutu: {} stopni".format(str(int(angle))), (50, 200), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0))

            if self.yacht_coordinates.azimuth != 0:
                cv2.putText(frame.image, "Azymut: " + str(self.yacht_coordinates.azimuth), (50, 150), cv2.FONT_HERSHEY_COMPLEX, 1,
                            255)

                cv2.putText(frame.image, "Azymut po korekcie: " + str(self.yacht_coordinates.azimuth), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1,
                            255)

            if self.buoy_coordinates.longitude != 0:
                cv2.putText(frame.image, "Wspolrzedne boi: " + str(self.buoy_coordinates), (50, 250),
                            cv2.FONT_HERSHEY_COMPLEX, 1,
                            255)

            cv2.imshow('detected', frame.image)

            if i % 10 == 0:
                if self.yacht_coordinates.azimuth != 0:
                    self.yacht_coordinates.azimuth = self.yacht_coordinates.azimuth + angle

                if self.yacht_coordinates.longitude != 0:
                    self.buoy_coordinates.set_from_vincenty_formulae(self.yacht_coordinates, distance)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                break

    @staticmethod
    def calculate_distance(mast_height, distance_from_camera):
        real_distance = math.sqrt(distance_from_camera**2 - mast_height**2)
        real_distance /= 1000
        return real_distance

    @staticmethod
    def calculate_angle(camera_angle, object_position, windows_width):
        pixel_angle = windows_width / camera_angle
        angle = (object_position / pixel_angle)
        half = (camera_angle / 2)
        if angle < half:
            angle = -1 * (half - angle)
        else:
            angle -= half
        return angle

    def clean(self):
        self.vc.release()
        cv2.destroyAllWindows()
