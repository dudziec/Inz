import cv2
import numpy as np


class Buoy:

    def __init__(self, width=0, height=0, distance=0):
        self.width = width
        self.height = height
        self.distance = distance
        # folder
        # self.ratio = 0.78
        # buoy
        self.ratio = 0.5
        # cube
        # self.ratio = 1
        self.ranges = []

    def set_size(self, height):
        self.width = height * self.ratio
        self.height = height

    def compute_distance(self, template):
        real_height = 1.5
        real_height_cube = 0.06
        real_height_folder = 0.32
        distance = 0
        f = 2.08
        f = (template.height * template.distance) / real_height
        if self.height != 0:
            distance = (real_height * f) / self.height
            print(str(distance) + "m")
        # distance = 50 / 1000
        return distance

    def get_pixel_size(self):
        pass

    def detect(self, frame, video):
        mask = frame.mask.copy()
        cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            if radius > 10:
                cv2.circle(frame.image, (int(x), int(y)), int(radius),
                           (0, 255, 255), 2)
                if video:
                    self.set_size(radius * 2)
                self.draw_rectangle(x, y, frame)
            detected = True
        else:
            detected = False
        return detected

    def draw_circle(self, frame):
        pass

    def draw_rectangle(self, x, y, frame):
        x1 = int(x - self.width / 2)
        x2 = int(x + self.width / 2)
        y1 = int(y - self.height / 2)
        y2 = int(y + self.height / 2)
        cv2.rectangle(frame.image, (x1, y1), (x2, y2), (255, 0, 0), 2)
