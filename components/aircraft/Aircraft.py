""" Module to hold Aircraft class """
import math
import logging

def avg_angle(a, b):
	if (abs(a-b) > 180.0):
		a += 360.0
	return ((a + b) / 2.0) % 360.0
		
arcmin = 1.0 / 60.0
dtr = math.pi / 180.0

class Aircraft:
	""" Class to represent aircraft"""

	#Current GPS position
	position = None
	last_pos_update = None

	#Altitude
	altitude = None
	#Last known ground speed and heading
	ground_speed = None
	ground_heading = None

	vertical_speed = None
	#Time in s of last state vector update
	last_vector_update = None

	icao_address = None
	callsign = None

	def __init__(self):
		pass

	def can_calc_update(self):
		return self.last_pos_update!=None and self.ground_speed!=None and self.ground_heading!=None and self.altitude!=None and self.vertical_speed!=None

	def merge(self, other, time, force_update = False):
		#if the other pos isn't more recent than us, do a motion model update
		if (self.can_calc_update() and self.last_pos_update >= other.last_pos_update):
			#Assume position has not been received, calculate update
			avg_gs = (self.ground_speed + other.ground_speed) / 2.0
			avg_heading = avg_angle(self.ground_heading, other.ground_heading)

			logging.info("Merging (" + self.icao_address + "):")
			logging.info("GS - Old: " + str(self.ground_speed) + " New: " + str(other.ground_speed) + " Avg: " + str(avg_gs))
			logging.info("Hdg - Old: " + str(self.ground_heading) + " New: " + str(other.ground_heading) + " Avg: " + str(avg_heading))
			logging.info("")

			self.ground_speed = avg_gs
			self.ground_heading = avg_heading

			self.update(time)
		else:
			if (other.last_pos_update != None):
				logging.info("Force Update (" + self.icao_address + "): ")
				logging.info("Calcpos: " + str(self.position) + ", " + str(self.altitude))
				logging.info("Actpos:  " + str(other.position) + ", " + str(other.altitude))
				logging.info("")

				self.position = other.position
				self.altitude = other.altitude
				self.last_act_pos = other.position
				self.last_pos_update = other.last_pos_update

				self.last_vector_update = other.last_pos_update

		self.ground_speed = other.ground_speed
		self.ground_heading = other.ground_heading

		if (other.vertical_speed!=None):
			self.vertical_speed = other.vertical_speed
		if (other.callsign!=None):
			self.callsign = other.callsign

	def update(self, time):
		""" propagate state vector from last update time to current
		time (time) """

		dT = time - self.last_vector_update

		#TODO: For better precision, take into account the oblateness of the earth
		#Or even better, use proj to convert into cartesian
		dLat = self.ground_speed * math.cos(self.ground_heading*dtr) * arcmin * dT / 3600.0
		dLong = self.ground_speed * math.sin(self.ground_heading*dtr) * arcmin * dT / 3600.0
		dLong /= math.cos(self.position[0]*dtr)

		new_Lat = self.position[0] + dLat
		new_Long = self.position[1] + dLong

		if (new_Lat > 90.0):
			new_Long = (new_Long + 180.0)
			new_Lat = 180.0 - new_Lat
		elif (new_Lat < -90.0):
			new_Long = (new_Long + 180.0)
			new_Lat = -180.0 - new_Lat
		
		if (new_Long < -180.0):
			new_Long = 360.0 - new_Long
		elif (new_Long > 180.0):
			new_Long = -360.0 + new_Long

		logging.info("Updating (" + self.icao_address + "):")
		logging.info("Time diff: " + str(dT))
		logging.info("dLat: " + str(dLat) + " dLong: " + str(dLong))
		logging.info("oldPos: " + str(self.position) + " newPos: " + str((new_Lat, new_Long)))
		logging.info("")

		self.position = (new_Lat, new_Long)

		self.altitude += self.vertical_speed * dT / 60.0

		self.last_vector_update = time

	def get_metric_pos(self):
		return (self.position[0], self.position[1], self.altitude*0.3048)

	def __str__(self):
		st = ""

		st += "Aircraft:{\n"

		st += "ADSB: " + str(self.icao_address) + " callsign: " + str(self.callsign) + "\n"
		st += "Position: " + str(self.position) + "\n"
		st += "Altitude: " + str(self.altitude) + "\n"
		st += "Last true pos update: " + str(self.last_pos_update) + "\n"
		st += "GS: " + str(self.ground_speed) + " Track: " + str(self.ground_heading) + "\n"
		st += "Vertical speed: " + str(self.vertical_speed) + "\n"
		st += "Last update: " + str(self.last_vector_update) + "\n}\n"

		return st

