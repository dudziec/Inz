import imutils
from inz.buoy import *


class Frame:

    def __init__(self, image):

        self.image = image
        self.hsv = self.to_hsv()
        self.width, self.height = image.shape[:-1]
        self.mask = None

    def erode(self, kernel_size, iterations=1):
        kernel = np.ones((kernel_size, kernel_size), np.float32)
        self.mask = cv2.erode(self.mask, kernel, iterations=iterations)

    def dilate(self, kernel_size, iterations=1):
        kernel = np.ones((kernel_size, kernel_size), np.float32)
        self.mask = cv2.dilate(self.mask, kernel, iterations=iterations)

    def opening(self, kernel_size, iterations=1):
        kernel = np.ones((kernel_size, kernel_size), np.float32)
        self.mask = cv2.morphologyEx(self.mask, cv2.MORPH_OPEN, kernel, iterations=iterations)

    def closing(self, kernel_size, iterations=1):
        kernel = np.ones((kernel_size, kernel_size), np.float32)
        self.mask = cv2.morphologyEx(self.mask, cv2.MORPH_CLOSE, kernel, iterations=iterations)

    def to_hsv(self):
        return cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)

    def in_range(self, ranges=list()):
        if len(ranges) >= 1:
            lwr = np.array(ranges[0][0])
            upr = np.array(ranges[0][1])
            self.mask = cv2.inRange(self.hsv, lwr, upr)

        if len(ranges) > 1:
            for i in range(1, len(ranges)):
                lwr = np.array(ranges[i][0])
                upr = np.array(ranges[i][1])
                temp_mask = cv2.inRange(self.hsv, lwr, upr)
                self.mask = cv2.bitwise_or(self.mask, temp_mask)

    def resize(self, new_width):
        self.image = imutils.resize(self.image, new_width)
        self.width, self.height = self.image.shape[:-1]

    def rotate(self, angle):
        self.image = imutils.rotate(self.image, angle=angle)
        self.mask = imutils.rotate(self.mask, angle=angle)

    def blur(self):
        self.hsv = cv2.GaussianBlur(self.hsv, (15, 15), 0)
