""" Module to support communication with 
an ASCOM Alpaca telescope """

import requests

class WebScope:
	""" Class to support communication with
	an ASCOM Alpaca telescope"""

	def __init__(self, endpoint, compliant = False):
		self.prefix = endpoint
		self.compliant = compliant

	def slew_to_altaz_deg(self, alt, az):
		r = requests.put(self.prefix + "/slewtoaltazasync", data = {"Altitude": alt, "Azimuth": az})

	def get_altaz_deg(self):
		if self.compliant:
			r_alt = requests.get(self.prefix + "/altitude")
			r_az = requests.get(self.prefix + "/azimuth")

			alt = r_alt.json()["Value"]
			az = r_az.json()["Value"]

			return alt, az

		else:
			r = requests.get(self.prefix + "/altaz")

			dic = r.json()
			return dic["Altitude"], dic["Azimuth"]

	def slew_rate_alt_deg(self, deg_per_sec):
		r = requests.put(self.prefix + "/altrate", data = {"AltitudeRate": deg_per_sec})

	def slew_rate_az_deg(self, deg_per_sec):
		r = requests.put(self.prefix + "/azrate", data = {"AzimuthRate": deg_per_sec})

	def slew_rate_deg(self, alt_rate, az_rate):
		r = requests.put(self.prefix + "/altazrate", data = {"AltitudeRate": alt_rate, "AzimuthRate": az_rate})

	def is_slewing(self):
		r = requests.get(self.prefix + "/slewing")

		return r.json()["Value"]

if __name__=="__main__":
	import time

	scope = WebScope("http://127.0.0.1:5000/api/v1/telescope/0")

	while True:
		scope.slew_to_altaz_deg(0.0, -30.0)
		while scope.is_slewing():
			print(scope.get_altaz_deg())
			time.sleep(0.2)

		scope.slew_to_altaz_deg(0.0, 0.0)
		while scope.is_slewing():
			print(scope.get_altaz_deg())
			time.sleep(0.2)

		time.sleep(3)

		scope.slew_to_altaz_deg(0.0, 30.0)
		while scope.is_slewing():
			print(scope.get_altaz_deg())
			time.sleep(0.2)

		scope.slew_to_altaz_deg(0.0, 0.0)
		while scope.is_slewing():
			print(scope.get_altaz_deg())
			time.sleep(0.2)

		time.sleep(3)