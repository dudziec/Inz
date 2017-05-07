from inz.frame import *
from inz.view import *


CAMERA_ANGLE = 50


class Video:
    def __init__(self, mode, op, yacht_coordinates, buoy_coordinates, calibration_coefficients):
        self.vc = cv2.VideoCapture(mode)
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

            # przetwarzanie co 6 klatek

            if i % 6 == 0:
                continue

            if not grabbed:
                print("Video not found!")
                break

            h, w = fr.shape[:-1]
            # fr = fr[0:h, 420:w - 420]

            frame.image = fr
            frame.mask = None
            frame.hsv = frame.to_hsv()
            frame.blur()
            frame.in_range(template.ranges)
            frame.rotate(0)

            for o in self.operations:
                o()

            x, y = self.buoy.detect(frame, True)
            distance = self.buoy.compute_distance(template)

            angle = self.calculate_angle(CAMERA_ANGLE, x, w)
            self.yacht_coordinates.azimuth = self.yacht_coordinates.azimuth + angle

            cv2.imshow('detected', frame.image)
            if i % 20 == 0:
                if self.yacht_coordinates.longitude != 0:
                    print("From video: ", self.yacht_coordinates, self.yacht_coordinates.azimuth)
                self.buoy_coordinates.set_from_vincenty_formulae(self.yacht_coordinates, distance)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                break

    def calculate_angle(self, camera_angle, object_position, windows_width):
        pixel_angle = windows_width / camera_angle
        angle = (object_position / pixel_angle)
        if angle < 25:
            angle = -1 * (25 - angle)
        else:
            angle -= 25
        return angle

    def clean(self):
        self.vc.release()
        cv2.destroyAllWindows()
