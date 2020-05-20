""" module to contain the CelestialCoordinateTransformer class"""

from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.time import Time
import astropy.units as u

import time

class CelestialCoordinateTransformer:

	#Local position in wgs84
	local_pos = None

	#Temperature in centigrade
	local_temp_c = None

	#Local pressure in millibar
	local_press_mbar = None

	def __init__(self, local_pos, local_temp_c=10.0, local_press_mbar=1010.0):
		self.local_pos = EarthLocation(lat=local_pos[0]*u.deg, lon=local_pos[1]*u.deg, height=local_pos[2]*u.m)

		self.set_local_conditions(local_temp_c, local_press_mbar)

	def set_local_conditions(self, local_temp_c, local_press_mbar):
		self.local_temp_c = local_temp_c
		self.local_press_mbar = local_press_mbar


	def apparent_to_altaz(self, apparent_ra, apparent_dec, JD=None):
		r_time = None
		if (JD==None):
			r_time = Time(time.time(), format="unix")
		else:
			r_time = Time(JD, format="jd")

		coord = SkyCoord(ra=apparent_ra*u.hour, dec=apparent_dec*u.degree, frame="itrs")

		altaz = coord.transform_to(AltAz(obstime=r_time, location=self.local_pos))

		print(altaz)

		

		



if __name__=="__main__":
	transformer = CelestialCoordinateTransformer([51.215745, 0.295962, 43.0], 37) #Scrubbed

	print(transformer.apparent_to_altaz(4.6174788889, 16.546825, JD=2458969.21332))
