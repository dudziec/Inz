from inz.frame import *
from inz.view import *



class Video:
    def __init__(self, mode, op, yacht_coordinates, buoy_coordinates):
        self.vc = cv2.VideoCapture(mode)
        self.buoy = Buoy()
        self.yacht_coordinates = yacht_coordinates
        self.buoy_coordinates = buoy_coordinates
        self.operations = op

    def capture(self, frame, template=None):
        i = 0
        while True:
            (grabbed, fr) = self.vc.read()
            i += 1
            # przetwarzanie co 6 klatki
            if i % 6 == 0:
                continue

            if not grabbed:
                print("Video not found!")
                break
            h, w = fr.shape[:-1]
            fr = fr[0:h, 420:w - 420]

            frame.image = fr
            frame.mask = None
            frame.hsv = frame.to_hsv()
            frame.blur()
            frame.in_range(template.ranges)
            frame.rotate(270)

            for o in self.operations:
                o()

            self.buoy.detect(frame, True)
            distance = self.buoy.compute_distance(template)

            # cv2.imshow('detected', frame.image)
            if i % 20 == 0:
                # TODO: dodać aktualny dystans!!!
                if self.yacht_coordinates.longitude != 0:
                    print("From video: ", self.yacht_coordinates, self.yacht_coordinates.azimuth)
                self.buoy_coordinates.set_from_vincenty_formulae(self.yacht_coordinates, distance)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                break

    def clean(self):
        self.vc.release()
        cv2.destroyAllWindows()
