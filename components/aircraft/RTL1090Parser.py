"""	Module to parse RTL1090 HTTP plane table data """
import requests_async as requests
import asyncio
import time as t
import logging
from ..aircraft.Aircraft import Aircraft
from ..aircraft.ADSBParser import ADSBParser

def to_float(st):
	if (len(st) > 0):
		return float(st)
	else:
		return 0.0

class RTL1090Parser(ADSBParser):
	""" Class to parse RTL1090 HTTP plane table data """

	def __init__(self, addr, poll_interval_ms=1000):
		super().__init__()

		self.addr = addr
		self.poll_interval_ms = poll_interval_ms

	async def message_loop(self):
		""" Queries RTL1090 table and returns an ICAO 24-bit indexed
		list of Aircraft objects """

		r =  await requests.get(self.addr)

		if r.status_code!=200:
			logging.error("Failed to get aircraft list from RTL1090!")
			return

		if r.text == "NODATA":
			return

		async with self.aircraft_lock:
			#Create temporary dictionary to hold new aircraft
			new_aircraft = {}

			#split table data format
			data = [line.split(":") for line in r.text.split("\n") if len(line) > 0]

			#Create aircraft object for each item
			current_time = t.time()

			for plane_data in data:
				plane = Aircraft()

				#Fill in aircraft data from table
				plane.position = (to_float(plane_data[8]), to_float(plane_data[9]))
				if plane.position != (0.0, 0.0):
					plane.last_pos_update = current_time

				plane.altitude = to_float(plane_data[13])

				plane.ground_speed = to_float(plane_data[27])
				plane.ground_heading = to_float(plane_data[22])

				plane.icao_address = plane_data[0]
				plane.callsign = plane_data[2]

				plane.last_vector_update = current_time

				plane.vertical_speed = to_float(plane_data[19])

				#Keep old pos update time if pos hasn't changed
				existing_plane = self.aircraft.get(plane.icao_address)

				if (existing_plane!=None and self.clear_aircraft_flag==False):
					if (existing_plane.position == plane.position):
						plane.last_pos_update = existing_plane.last_pos_update

				new_aircraft[plane.icao_address] = plane
			
			self.aircraft = new_aircraft
			self.clear_aircraft_flag = False
					



if __name__=="__main__":
	parser = RTL1090Parser("http://127.0.0.1:31008/table2")

	asyncio.run(parser.message_loop())

	planes = parser.get_aircraft()
	for plane in planes:
		print(plane)