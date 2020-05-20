""" module to contain AircraftManager class"""

from ..aircraft.Aircraft import Aircraft
import time
import logging
import asyncio
import threading
import copy

class AircraftManager:
	""" class to manage and update aircraft positions """

	aircraft_source = None

	#dictionary to store aircraft
	aircraft = None
	#thread level lock for dictionary access
	aircraft_lock = None
	#asyncio lock for own dictionary access
	async_aircraft_lock = None

	motion_model_rate_ms = 10.0

	#Switch to command shutdown of the update thread
	run_update_thread = False

	def __init__(self, aircraft_source):
		self.aircraft_source = aircraft_source

		self.aircraft = {}
		self.aircraft_lock = threading.Lock()
		self.async_aircraft_lock = asyncio.Lock()

		#WARNING this is for the nasty update function hack!
		#self.event_loop = None

	async def source_poll_loop(self):
		while self.run_update_thread:
			#Allow plane source to poll for data
			await self.aircraft_source.message_loop()

			#Acquire locks to modify aircraft data in source and ourselves
			async with self.aircraft_source.aircraft_lock:
				#Ensure only one coroutine can try to acquire the thread lock
				async with self.async_aircraft_lock:
					#Acquire thread level lock
					with self.aircraft_lock:
						#Get REFERENCE to plane data from source
						new_aircraft = self.aircraft_source.get_aircraft()

						cur_time = time.time()

						#Loop through the source planes
						for icao_address, plane in new_aircraft.items():
							
							if (self.aircraft.get(icao_address)==None):
								#New plane with position, copy it in
								if plane.last_pos_update!=None:
									self.aircraft[icao_address] = copy.deepcopy(plane)
									print("New plane: " + icao_address)
									print(plane)
							else:
								#Existing plane, merge the new data, possibly doing
								#a motion update
								self.aircraft[icao_address].merge(plane, cur_time)
								#print("Merge: " + icao_address)

			#Sleep for source poll interval
			await asyncio.sleep(self.aircraft_source.poll_interval_ms / 1000.0)

	async def motion_model_loop(self):
		while self.run_update_thread:
			#Ensure only one coroutine can try to acquire the thread lock
			async with self.async_aircraft_lock:
				#Acquire lock to modify own planes
				with self.aircraft_lock:
					cur_time = time.time()

					#Do a motion update for all our planes
					for plane in self.aircraft.values():
						if (plane.can_calc_update()):
							plane.update(cur_time)

			#Sleep for motion update interval
			await asyncio.sleep(self.motion_model_rate_ms / 1000.0)

	async def update_loop_async(self):
		await asyncio.gather(self.motion_model_loop(), self.source_poll_loop())
		print("We done")

	def enter_update_loop(self):
		""" Enters the infinite update loop, should be in a new
		thread for this """

		print("Starting aircraft update manager loop")

		self.run_update_thread = True
		asyncio.run(self.update_loop_async())

	def stop_update_loop(self):
		self.run_update_thread = False

	def get_plane(self, icao_address):
		plane = None
		
		with self.aircraft_lock:
			plane = copy.deepcopy(self.aircraft.get(icao_address))

		return plane

	def get_planes(self):
		planes = None

		with self.aircraft_lock:
			planes = copy.deepcopy(self.aircraft)

		return planes

	def get_plane_list(self):
		plane_list = None

		with self.aircraft_lock:
			plane_list = [icao_address for icao_address in self.aircraft.keys()]

		return plane_list

	def clear_plane_list(self):
		with self.aircraft_lock:
			self.aircraft = {}
			self.aircraft_source.clear_aircraft()

	# def update(self):
	# 	"""WARNING, for god's sake don't use this function again,
	# 	it's hacked together to support the new async stuff"""

	# 	if self.event_loop==None:
	# 		self.event_loop = asyncio.get_event_loop()

	# 	self.event_loop.run_until_complete(self.aircraft_source.message_loop())
	# 	new_aircraft = self.aircraft_source.get_aircraft()

	# 	cur_time = time.time()

	# 	#Loop through existing planes
	# 	for icao_address, plane in self.aircraft.items():
	# 		new_plane = new_aircraft.get(icao_address)

	# 		#If we have an update to merge, do so, then
	# 		#remove from list so we can add new ones
	# 		if new_plane!=None:
	# 			plane.merge(new_plane)
	# 			del new_aircraft[icao_address]
	# 		else:
	# 			plane.update(cur_time)

	# 	#add in the completely new planes that have positions
	# 	for icao_address, new_plane in new_aircraft.items():
	# 		if new_plane.last_pos_update != None:
	# 			self.aircraft[icao_address] = new_plane
	
	# def motion_update(self):
	# 	""" Update all planes with motion models """

	# 	cur_time = time.time()

	# 	for plane in self.aircraft.values():
	# 		plane.update(cur_time)
		

if __name__=="__main__":
	from ..aircraft.RTL1090Parser import RTL1090Parser
	from ..aircraft.Dump1090Parser import Dump1090Parser

	#parser = RTL1090Parser("http://127.0.0.1:31008/table2")
	parser = Dump1090Parser("127.0.0.1", 30003)
	manager = AircraftManager(parser)

	update_thread = threading.Thread(target = manager.enter_update_loop)
	update_thread.start()

	while True:
		for plane in manager.get_planes().values():
			print(plane)

		time.sleep(2)