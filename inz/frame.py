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

    def in_range(self):
        lwr1 = np.array([0, 100, 140])
        upr1 = np.array([25, 240, 240])

        lwr2 = np.array([170, 100, 120])
        upr2 = np.array([200, 240, 240])

        mask1 = cv2.inRange(self.hsv, lwr1, upr1)
        mask2 = cv2.inRange(self.hsv, lwr2, upr2)

        self.mask = cv2.bitwise_or(mask1, mask2)

    def resize(self, new_width):
        self.image = imutils.resize(self.image, new_width)
        self.width, self.height = self.image.shape[:-1]

    def rotate(self, angle):
        self.image = imutils.rotate(self.image, angle=angle)

    def blur(self):
        self.hsv = cv2.GaussianBlur(self.hsv, (15, 15), 0)
