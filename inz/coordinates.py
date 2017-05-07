from random import randint, random
from math import asin, cos, pi, sin, radians, degrees
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
        """

        :param coordinates:
        :param azimuth:
        :return:
        """
        self.latitude = coordinates[0]
        self.longitude = coordinates[1]
        self.azimuth = azimuth

    def set_random_buoy_coordinates(self, yacht_coordinates):
        """

        :param yacht_coordinates:
        :return:
        """
        shift = randint(0, 100) / 100000
        self.latitude = yacht_coordinates.latitude + shift
        self.longitude = yacht_coordinates.longitude + shift

    def __str__(self):
        return "{}, {}".format(self.latitude, self.longitude)

    # def set_coordinates_from_haversine_formula(self, initial_coordinates, distance):
    #     """ Funkcja obliczająca współrzędne za pomocą wzoru Haversine.
    #
    #     Funkcja
    #
    #     :param initial_coordinates: współrzędne jachtu
    #     :param azimuth: kąt
    #     :param distance: odległość
    #     :return:
    #     """
    #     # azimuth = initial_coordinates.azimuth -
    #     azimuth = ((initial_coordinates.azimuth - 360) % 360) - 90
    #
    #     radians_latitude = radians(initial_coordinates.latitude)
    #     radians_longitude = radians(initial_coordinates.longitude)
    #
    #     radians_azimuth = radians(azimuth)
    #     radians_distance = distance / _EARTH_RADIUS
    #
    #     radians_latitude_tmp = asin(sin(radians_latitude) * cos(radians_distance)
    #                                 + cos(radians_latitude) * sin(radians_distance) * cos(radians_azimuth))
    #
    #     if cos(radians_latitude_tmp) == 0 or abs(cos(radians_latitude_tmp)) < _EPSILON:
    #         radians_longitude_tmp = radians_latitude_tmp
    #     else:
    #         radians_longitude_tmp = ((radians_longitude - asin(sin(radians_azimuth) * sin(radians_distance) /
    #                                                            cos(radians_latitude_tmp)) + pi) % (2 * pi)) - pi
    #
    #     self.latitude = degrees(radians_latitude_tmp)
    #     self.longitude = degrees(radians_longitude_tmp)

    def set_from_vincenty_formulae(self, initial_coordinates, distance):
        point = VincentyDistance(kilometers=distance).destination(Point(initial_coordinates.latitude,
                                                                        initial_coordinates.longitude),
                                                                  initial_coordinates.azimuth)
        self.latitude = point.latitude
        self.longitude = point.longitude
