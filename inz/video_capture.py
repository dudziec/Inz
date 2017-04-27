from inz.frame import *
from inz.view import *


class Video:
    def __init__(self, mode, op):
        self.vc = cv2.VideoCapture(mode)
        self.buoy = Buoy()
        self.operations = op

    def capture(self, frame, template=None):
        while True:
            (grabbed, fr) = self.vc.read()

            if not grabbed:
                print("Video not found!")
                break
            h, w = fr.shape[:-1]
            fr = fr[0:h, 420:w - 420]
            # self.operations[0]()
            # frame = Frame(fr)
            frame.image = fr
            frame.rotate(0)
            frame.blur()
            frame.in_range(template.ranges)
            frame.closing(10, 3)

            self.buoy.detect(frame, True)
            self.buoy.compute_distance(template)
            cv2.imshow('mask', frame.mask)
            cv2.imshow('detected', frame.image)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                break

    def clean(self):
        self.vc.release()
        cv2.destroyAllWindows()
