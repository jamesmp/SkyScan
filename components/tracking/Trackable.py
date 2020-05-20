""" module implementing abstract Trackable Class """

class Trackable:
    """ Abstract class representing any trackable object
    e.g. plane, star, satellite """

    def __init__(self):
        raise NotImplementedError()

    def get_position(self):
        """ get position of object in epsg:4979 Lat/Long/ellipsoid height"""
        raise NotImplementedError

    def get_name(self):
        return "No Name"

    def is_tracking(self):
        raise NotImplementedError