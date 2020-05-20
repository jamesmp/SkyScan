""" module implementing the TrackableAircraft class"""

from ..tracking.Trackable import Trackable
from ..tracking.Position import Position

class TrackableAircraft(Trackable):

    #The aircraft manager instance to query for updates
    aircraft_manager = None

    icao_address = None

    def __init__(self, aircraft_manager, icao_address):
        self.aircraft_manager = aircraft_manager
        self.icao_address = icao_address

    def get_position(self):
        plane = self.aircraft_manager.get_plane(self.icao_address)

        if plane==None:
            return None

        if plane.last_pos_update==None:
            return None

        pos = plane.get_metric_pos()

        return Position(Position.TYPE_LATLONG, lat=pos[0], long=pos[1], height=pos[2])

    def get_name(self):
        return self.icao_address

    def is_tracking(self):
        return self.aircraft_manager.get_plane(self.icao_address)!=None