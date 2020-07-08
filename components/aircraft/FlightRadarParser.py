from ..aircraft.Aircraft import Aircraft
from ..aircraft.ADSBParser import ADSBParser
from datetime import datetime
import asyncio
import re
from requests_async import Session
import json

class FlightRadarParser(ADSBParser):
    """ Class to Pull aircraft from flightradar24 """


    def __init__(self, lat, long, bound_range = 2.0, endpoint = "https://data-live.flightradar24.com/zones/fcgi/feed.js"):
        super().__init__()

        self.endpoint = endpoint
        self.poll_interval_ms = 1000  

        self.query_lat = lat
        self.query_long = long
        self.bound_range = bound_range

    async def get_data(self):
        session = Session()

        headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0',
                'Origin': 'https://www.flightradar24.com',
                'Referer': 'https://www.flightradar24.com'
        }

        lat_pair = (self.query_lat + self.bound_range / 2.0, self.query_lat - self.bound_range / 2.0)
        long_pair = (self.query_long - self.bound_range / 2.0, self.query_long + self.bound_range / 2.0)

        bounds = "{lat_pair[0]:.2f},{lat_pair[1]:.2f},{long_pair[0]:.2f},{long_pair[1]:.2f}".format(lat_pair=lat_pair, long_pair=long_pair)

        params = {
            "bounds": bounds,
            "faa": 1,
            "satellite": 1,
            "mlat": 1,
            "flarm": 1,
            "adsb": 1,
            "gnd": 0,
            "air": 1,
            "vehicles": 1,
            "estimated": 1,
            "maxage": 14400,
            "gliders": 1
        }
        
        res = await session.get(self.endpoint, params=params, headers=headers)

        data = json.loads(res.content)

        aircraft = {}
        for k, v in data.items():
            if (k != "full_count" and k != "version" and k != "stats"):
                plane = Aircraft()

                plane.icao_address = v[0]
                plane.position = (v[1], v[2])
                plane.ground_heading = v[3]
                plane.altitude = v[4]
                plane.ground_speed = v[5]
                plane.vertical_speed = 0 #Annoying, not in the data
                plane.callsign = v[16]

                plane.last_pos_update = v[10]
                plane.last_vector_update = v[10]

                aircraft[v[0]] = plane

                print("Plane: " + str(plane))

        return aircraft


    async def message_loop(self):
        
        data = await self.get_data()

        async with self.aircraft_lock:
            if self.clear_aircraft_flag:
                self.aircraft = {}
                self.clear_aircraft_flag = False

            self.aircraft = data
            # for icao_address, new_plane in data.items():

            #     plane = self.aircraft.get(icao_address)
            #     if (plane!=None):
            #         #Vector update time is always the most recent
            #         if new_plane.last_vector_update < plane.last_vector_update:
            #             new_plane.last_vector_update = plane.last_vector_update

            #     plane = new_plane

            #     self.aircraft[icao_address] = plane


async def loop():
    while True:
        await parser.message_loop()

if __name__=="__main__":
    parser = FlightRadarParser(51.217, 0.280)

    asyncio.run(loop())