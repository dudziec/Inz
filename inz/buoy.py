import cv2
import numpy as np


class Buoy:

    def __init__(self, d=0):
        self.width = 0
        self.height = 0
        self.distance = d
        self.ratio = 0.5

    def set_size(self, height):
        self.width = height * self.ratio
        self.height = height

    def compute_distance(self, template):
        f = (template.height * template.distance) / 1.5
        distance = (1.5 * f) / self.height
        return distance

    def get_pixel_size(self):
        pass

    def detect(self, frame):
        center = None
        cnts = cv2.findContours(frame.mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            if radius > 10:
                cv2.circle(frame.image, (int(x), int(y)), int(radius),
                           (0, 255, 255), 2)
                cv2.circle(frame.image, center, 5, (0, 0, 255), -1)
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

