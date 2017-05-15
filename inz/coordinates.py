# -*- coding: utf-8 -*-
from random import randint, random
from numpy.random.mtrand import randint
from geopy.distance import VincentyDistance
from geopy.distance import Point

_EARTH_RADIUS = 6371
_EPSILON = 0.00000001


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

    def set_from_vincenty_formulae(self, initial_coordinates, distance):
        azimuth = abs((initial_coordinates.azimuth - 360.0) - 90)
        point = VincentyDistance(kilometers=distance).destination(Point(initial_coordinates.latitude,
                                                                        initial_coordinates.longitude),
                                                                  azimuth)
        self.latitude = point.latitude
        self.longitude = point.longitude
