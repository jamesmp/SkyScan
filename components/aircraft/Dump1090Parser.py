from ..aircraft.Aircraft import Aircraft
from ..aircraft.ADSBParser import ADSBParser
from datetime import datetime
import asyncio
import re

def to_float(st):
    if (len(st) > 0):
        return float(st)
    else:
        return 0.0

timestamp_re = re.compile(r"([0-9]+)/([0-9]+)/([0-9]+)T([0-9]+):([0-9]+):([0-9]+).([0-9]+)")

class Dump1090Parser(ADSBParser):
    """ Class to interpret Dump1090 plane messages """

    #asyncio stream reader/writer combo for TCP socket
    sock_reader = None
    sock_writer = None

    def __init__(self, addr, port):
        super().__init__()

        self.addr = addr
        self.port = port
        self.poll_interval_ms = 0

    def decode_date_time(self, date_str, time_str):
        date_groups = timestamp_re.match(date_str + "T" + time_str).groups()

        year = int(date_groups[0])
        month = int(date_groups[1])
        day = int(date_groups[2])

        hour = int(date_groups[3])
        minute = int(date_groups[4])
        second = int(date_groups[5])
        microsecond = int(date_groups[6]) * 1000

        date = datetime(year, month, day, hour, minute, second, microsecond)
        unix_time = date.timestamp()

        return unix_time
        

    async def message_loop(self):
        if (self.sock_reader==None or self.sock_writer==None):
            try:
                self.sock_reader, self.sock_writer = await asyncio.open_connection(self.addr, self.port)
            except ConnectionRefusedError:
                print("Dump1090 connection refused")
                await asyncio.sleep(1)
                return

        line = (await self.sock_reader.readline()).decode("utf-8").replace("\r", "").replace("\n", "")
        data = line.split(",")

        if (data[0]!="MSG"):
            return

        async with self.aircraft_lock:
            if self.clear_aircraft_flag:
                self.aircraft = {}
                self.clear_aircraft_flag = False

            msg_type = data[1]
            icao_address = data[4]
            time = self.decode_date_time(data[6], data[7])

            plane = self.aircraft.get(icao_address)
            if (plane==None):
                plane = Aircraft()
                plane.icao_address = icao_address

            if (msg_type=="4" or msg_type=="2"):
                #Velocity data
                gs = data[12]
                trk = data[13]

                plane.ground_speed = float(gs)
                plane.ground_heading = float(trk)

            if (msg_type=="4"):
                vr = data[16]

                if (len(vr)>0):
                    plane.vertical_speed = float(vr)

            if (msg_type=="2" or msg_type=="3"):
                alt = data[11]
                lat = data[14]
                long = data[15]

                plane.altitude = float(alt)
                plane.position = (float(lat), float(long))
                plane.last_pos_update = time
                plane.last_vector_update = time

            if (msg_type=="5" or msg_type=="6" or msg_type=="7"):
                alt = data[11]

                if (len(alt) > 0):
                    plane.altitude = float(alt)
            
            if (msg_type=="1"):
                cs = data[10]

                plane.callsign = cs

            self.aircraft[icao_address] = plane


async def loop():
    while True:
        await parser.message_loop()

if __name__=="__main__":
    parser = Dump1090Parser("127.0.0.1", 30003)

    asyncio.run(loop())
        