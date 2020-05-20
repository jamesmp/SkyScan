""" module implementing abstract ADSBParser class"""

import asyncio

class ADSBParser:

    #The rate at which message_loop should be called
    poll_interval_ms = 1000

    #Dictionary containing the current aircraft data
    aircraft = None

    #Asyncio lock gating access to the aircraft dictionary
    aircraft_lock = None

    clear_aircraft_flag = False

    def __init__(self):
        self.aircraft = {}
        self.aircraft_lock = asyncio.Lock()

    async def message_loop(self):
        """ async loop for fetching messages from the data source """
        raise NotImplementedError

    def get_aircraft(self):
        """ MUST be called from an async method 
		taking the aircraft dictionary lock"""

        return self.aircraft

    def clear_aircraft(self):
        self.clear_aircraft_flag = True