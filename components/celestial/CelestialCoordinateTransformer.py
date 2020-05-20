""" module to contain the CelestialCoordinateTransformer class"""

import time
import math

DTR = math.pi / 180.0
RTD = 1.0 / DTR

class CelestialCoordinateTransformer:

	#Local position in wgs84
	local_pos = None

	#number of leap seconds (TAI-UTC)
	leap_seconds = None

	#Temperature in centigrade
	local_temp_c = None

	#Local pressure in millibar
	local_press_mbar = None

	def __init__(self, local_pos, leap_seconds=37, local_temp_c=10.0, local_press_mbar=1010.0):
		self.local_pos = local_pos

		self.set_local_conditions(local_temp_c, local_press_mbar)
		self.leap_seconds = leap_seconds

	def set_local_conditions(self, local_temp_c, local_press_mbar):
		self.local_temp_c = local_temp_c
		self.local_press_mbar = local_press_mbar

	def calc_JD(self):
		utc = time.gmtime()
		
		#Meeus is wrongus, his formula seems to be from 0h
		day_fraction = (utc.tm_hour + utc.tm_min / 60.0 + utc.tm_sec / 3600.0) / 24.0
		
		month = utc.tm_mon
		year = utc.tm_year
		if (month <= 2):
			year = year - 1
			month = month + 12

		A = year//100
		B = 2-A+(A//4)
		
		JD0h = math.floor(365.25*(year+4716)) + math.floor(30.6001*(month+1)) + utc.tm_mday + B - 1524.5 #JD at midnight

		JD = JD0h + day_fraction

		return JD

	def calc_JDE(self, JD=None):
		if JD==None:
			JD = self.calc_JD

		return JD + (self.leap_seconds + 32) / 86400 #Add 32 leap seconds from JDE start to TAI start of 

	def get_gha(self, apparent_ra, apparent_dec, JD=None):
		if (JD==None):
			JD = self.calc_JD()      #Julian date in days

		JDE = self.calc_JDE(JD)  #Julian date corrected for leap seconds

		TE = (JDE-2451545.0) / 36525.0 #Julian centuries since 2000 Jan 0.5 in TDT (linear time)
		T =  (JD -2451545.0) / 36525.0 #Julian centuries since 2000 Jan 0.5 in UT1 (sunny time...)

		Td = T*36525.0 #Julian days since 2000 Jan 0.5 in UT1

		eps = (84381.448 - 46.815*TE - 0.00059*TE*TE + 0.001813*TE*TE*TE)/3600.0 #Obliquity of date
		eps += 0.0026*math.cos(DTR*(125.0-0.05295*Td)) + 0.0002*math.cos(DTR*(200.9+1.97129*Td))
		delta_psi = (-0.0048)*math.sin((125.0-0.05295*Td)*DTR) + (-0.1114)*math.sin((200.9 + 1.97129*Td)*DTR) #Nutation in longitude

		#Calculate earth centric GHA
		gha_true = (280.46061837 + 360.98564736629*(JD-2451545) + 0.000387933*T*T - T*T*T/38710000.0) % 360.0
		#gha_true = (gha_mean + delta_psi*math.cos(eps*DTR)) #Sidereal time at greenwich

		gha_object = (gha_true - apparent_ra) % 360.0

		return gha_object

	def apparent_to_altaz(self, apparent_ra, apparent_dec, JD=None):
		
		gha_object = self.get_gha(apparent_ra, apparent_dec, JD)

		#Calculate observer centric LHA
		lha = (gha_object + self.local_pos[1])

		#Calculate true alt/az
		alt = RTD*math.asin(math.sin(DTR*apparent_dec)*math.sin(DTR*self.local_pos[0]) + math.cos(DTR*self.local_pos[0])*math.cos(DTR*apparent_dec)*math.cos(DTR*lha));
		az = RTD*math.acos((math.sin(DTR*apparent_dec)-math.sin(DTR*self.local_pos[0])*math.sin(DTR*alt))/(math.cos(DTR*self.local_pos[0])*math.cos(DTR*alt)));
		if (lha<180.0):
			az = 360.0-az;

		#Correct alt for refraction
		ref = 1.02 / math.tan(DTR*(alt + (10.3 / (alt + 5.11))));
		ref *= (0.00467*self.local_press_mbar / (273.0 + self.local_temp_c));
		alt = alt + ref

		return (alt, az)

	def apparent_to_latlong(self, apparent_ra, apparent_dec, JD=None):

		gha_object = self.get_gha(apparent_ra, apparent_dec, JD)

		long = -gha_object
		if long > 180.0:
			long -= 360.0

		lat = apparent_dec

		return (lat, long)



if __name__=="__main__":
	transformer = CelestialCoordinateTransformer([51.215745, 0.295962, 43.0], 37) #Scrubbed

	print(transformer.apparent_to_altaz(59.735266666666666666666666666667, -13.45505, JD=(2458970.07369)))
