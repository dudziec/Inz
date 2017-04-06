from inz.frame import *


class Video:
    def __init__(self, mode):
        self.vc = cv2.VideoCapture(mode)
        self.buoy = Buoy()

    def capture(self, template):
        while True:
            (grabbed, fr) = self.vc.read()

            if not grabbed:
                break
            h, w = fr.shape[:-1]
            fr = fr[0:h, 420:w - 420]

            # h, w = fr.shape[:-1]

            # roi1 = fr[0:int((h/2 + h/5)), 0:int((w/2 + w/5))]
            # roi3 = fr[int((h/2 - h/5)):h, 0:int((w/2 + w/5))]
            # roi4 = fr[int((h/2 - h/5)):h, int((w/2 - w/5)):w]
            # roi2 = fr[0:int((h/2 + h/5)),  int((w/2 - w/5)):w]

            frame = Frame(fr)
            frame.rotate(0)
            frame.blur()
            frame.in_range()
            # frame.erode(10, 1)
            # frame.closing(5, 10)
            # frame.dilate(10, 2)

            self.buoy.detect(frame)
            print(int(self.buoy.compute_distance(template)), " m")
            # cv2.imshow('ROI1', roi1)
            # cv2.imshow('ROI2', roi2)
            # cv2.imshow('ROI3', roi3)
            # cv2.imshow('ROI4', roi4)
            cv2.imshow('Video', frame.image)

            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                break

    def clean(self):
        self.vc.release()
        cv2.destroyAllWindows()

