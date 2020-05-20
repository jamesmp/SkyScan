""" module to contain the TrackableCelestial class """

from ..tracking.Trackable import Trackable
from ..tracking.Position import Position
from ..celestial.CelestialCoordinateTransformer import CelestialCoordinateTransformer

class TrackableCelestial(Trackable):
	#The alpaca server instance to query for updates
	alpaca_server = None

	def __init__(self, alpaca_server):
		self.alpaca_server = alpaca_server
		self.transformer = CelestialCoordinateTransformer([0.0, 0.0, 0.0])

	def get_position(self):
		#Get RA/DEC from alpaca server
		ra, dec = self.alpaca_server.get_ra_dec()

		#Transform
		lat, long = self.transformer.apparent_to_latlong(ra, dec)

		#print("radec: " + str((ra, dec)))
		#print("latlong: " + str((lat, long)))
		#print("altaz: " + str(self.transformer.apparent_to_altaz(ra, dec)))

		return Position(Position.TYPE_LATLONG, lat=lat, long=long, height=100000000000.0)

	def get_name(self):
		return "Celestial"

	def is_tracking(self):
		return True