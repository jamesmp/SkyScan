from aircraft.AircraftManager import AircraftManager
from aircraft.RTL1090Parser import RTL1090Parser
from interface.WebScope import WebScope
from transformer.LocalCoordinateTransformer import LocalCoordinateTransformer
from solver.MountModel import MountModel
from solver.PointingSolver import PointingSolver

import time
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)

#Aircraft Source
parser = RTL1090Parser("http://127.0.0.1:31008/table2")
manager = AircraftManager(parser)

#Telescope Driver
scope_driver = WebScope("http://127.0.0.1:5000/api/v1/telescope/0")

#Telescope Solver
scope_model = MountModel()
point_solver = PointingSolver(scope_model)

#Point Transformer
point_transformer = LocalCoordinateTransformer([51.215745, 0.295962, 43.0]) #Scrubbed

chosen_id = "780D9C"
while True:
    manager.update()

    if chosen_id==None:
        try:
            chosen_id = iter(manager.aircraft.keys()).__next__()
        except:
            time.sleep(1)
    else:
        plane = manager.aircraft.get(chosen_id)
        
        if plane!=None:
            plane_pos = np.array(plane.get_metric_pos())
            local_pos = point_transformer.transform_to_local(plane_pos)

            altaz = point_solver.get_point_altaz(local_pos)

            print(plane.callsign + " adsb: " + plane.icao_address)
            print(altaz)

            scope_driver.slew_to_altaz_deg(altaz[0], altaz[1])

        time.sleep(0.2)

    

    