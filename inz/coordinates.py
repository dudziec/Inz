from random import randint, random

from numpy.random.mtrand import randint


class Coordinates:

    def __init__(self):
        self.latitude = 0
        self.longitude = 0
        self.azimuth = 0

    def set_coordinates(self, coordinates, azimuth=0):
        self.latitude = coordinates[0]
        self.longitude = coordinates[1]
        self.azimuth = azimuth


    def set_random_buoy_coordinates(self, yacht_coordinates):
        shift = randint(0, 100) / 100000
        self.latitude = yacht_coordinates.latitude + shift
        self.longitude = yacht_coordinates.longitude + shift

    def __str__(self):
        return "{}, {}".format(self.latitude, self.longitude)
