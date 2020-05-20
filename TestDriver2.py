from components.aircraft.AircraftManager import AircraftManager
from components.aircraft.RTL1090Parser import RTL1090Parser
from components.aircraft.Dump1090Parser import Dump1090Parser
from components.interface.WebScope import WebScope
from components.transformer.LocalCoordinateTransformer import LocalCoordinateTransformer

from components.tracking.ObjectTracker import ObjectTracker
from components.aircraft.TrackableAircraft import TrackableAircraft

import time
import numpy as np
import logging
import threading

#logging.basicConfig(level=logging.INFO)

#Aircraft Source
#parser = RTL1090Parser("http://127.0.0.1:31008/table2")
parser = Dump1090Parser("127.0.0.1", 30003)
manager = AircraftManager(parser)

manager_thread = threading.Thread(target=manager.enter_update_loop)
manager_thread.start()

#Telescope Driver
scope_driver = WebScope("http://127.0.0.1:5000/api/v1/telescope/0")

#Point Transformer
point_transformer = LocalCoordinateTransformer([51.215745, 0.295962, 43.0]) #Scrubbed

#Tracker
tracker = ObjectTracker(point_transformer, scope_driver)


chosen_id = "3C5430"
aircraft = TrackableAircraft(manager, chosen_id)

tracker.set_tracked_object(aircraft)

while True:
    if aircraft.is_tracking():
        tracker.run()

    print(aircraft.get_position())
    print(tracker.get_last_motor_angle())

    time.sleep(0.2)

    

    