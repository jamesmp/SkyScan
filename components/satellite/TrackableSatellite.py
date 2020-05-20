""" module to implement TrackableSatellite class """

from ..tracking.Trackable import Trackable
from ..tracking.Position import Position
import requests

class TrackableSatellite(Trackable):

	#Address to query for DDE bridge
	uri = None

	#Name of satellite being tracked
	name = "Unknown"

	def __init__(self, uri):
		self.uri = uri

	def get_position(self):
		r = requests.get(self.uri)

		data = r.json()

		self.name = data["SN"]
		
		alt = float(data["EL"])
		az = float(data["AZ"])

		return Position(Position.TYPE_ALTAZ, alt=alt, az=az)

	def get_name(self):
		return self.name

	def is_tracking(self):
		return True