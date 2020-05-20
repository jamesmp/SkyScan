""" module to implement ObjectTracker class"""

from ..solver.MountModel import MountModel
from ..solver.PointingSolver import PointingSolver
from ..tracking.Trackable import Trackable
from ..tracking.Position import Position

from collections import namedtuple

class ObjectTracker:
    """ Class to manage the real-time tracking of some 
    trackable object e.g. plane, star, satellite"""

    #The Trackable instance currently being tracked
    tracked_object = None

    #The LocalCoordinateTransformer instance to use
    local_coordinate_transformer = None

    #The pointing solver to use for AltAz derivation
    pointing_solver = None

    #The telescope driver interface to use
    scope_driver = None

    #The motor offsets to add to calculated angles
    tracking_offset = (0.0, 0.0)

    #The current calibration parameters
    mount_model = None

    #The most recent motor angle command
    last_motor_angle = (0.0, 0.0)

    def __init__(self, local_coordinate_transformer, scope_driver, mount_model=MountModel()):
        self.local_coordinate_transformer = local_coordinate_transformer
        self.scope_driver = scope_driver

        self.mount_model = mount_model
        self.pointing_solver = PointingSolver(mount_model)

    def set_tracked_object(self, obj):
        self.tracked_object = obj

    def set_mount_model(self, mount_model):
        self.mount_model = mount_model.copy()
        self.pointing_solver.set_model(self.mount_model)

    def set_tracking_offset(self, alt, az):
        self.tracking_offset = (alt, az)

    def add_tracking_offset(self, dAlt, dAz):
        self.tracking_offset = (self.tracking_offset[0] + dAlt, self.tracking_offset[1] + dAz)

    def get_tracking_offset(self):
        return self.tracking_offset
    
    def is_tracking(self):
        if self.tracked_object==None:
            return False

        return self.tracked_object.is_tracking()

    def get_trackable_position(self):
        """ get current LOCAL object position from the attached trackable """
        if self.tracked_object==None:
            return None

        #Get position from trackable in epsg:4979
        obj_pos = self.tracked_object.get_position()

        if obj_pos==None:
            return None

        if (obj_pos.pos_type == Position.TYPE_LATLONG):
            #Transform to local cartesian space
            local_pos = self.local_coordinate_transformer.transform_to_local(obj_pos.as_tuple())

            obj_pos = Position(Position.TYPE_CARTESIAN, x=local_pos[0], y=local_pos[1], z=local_pos[2])

        return obj_pos

    def get_tracked_object(self):
        return self.tracked_object

    def get_model(self):
        return self.mount_model.copy()

    def run(self):
        """ calculate a new state vector and send to
        scope driver """

        #Get cartesian coordinates of object
        local_pos = self.get_trackable_position()
        
        if local_pos==None:
            return

        alt = None
        az = None

        if (local_pos.pos_type == Position.TYPE_CARTESIAN):
            #Get unmodified AltAz
            alt, az = self.pointing_solver.get_point_altaz(local_pos.as_tuple())
        elif (local_pos.pos_type == Position.TYPE_ALTAZ):
            alt = local_pos.alt
            az = local_pos.az
        else:
            raise RuntimeError("Unusable local position type")

        #Add modifiers
        alt += self.tracking_offset[0]
        az += self.tracking_offset[1]

        if (abs(alt) > 90.0):
            az += 180.0

            if alt > 0.0:
                alt = 180.0 - alt
            else:
                alt = -180.0 - alt

        az = az % 360.0

        #Drive scope
        self.scope_driver.slew_to_altaz_deg(alt, az)

        self.last_motor_angle = (alt, az)

    TrackerState = namedtuple("TrackerState", "local_pos alt az")

    def get_state(self):
        """ Get the current state information. Trackable position and exact motor angles"""
        local_pos = self.get_trackable_position()
        alt, az = self.scope_driver.get_altaz_deg()

        self.last_motor_angle = (alt, az)

        #Might be better if this was an exception
        if local_pos==None:
            raise RuntimeError("Object tracker cannot get position from trackable")

        return self.TrackerState(local_pos, alt, az)

    def get_last_motor_angle(self):
        return self.last_motor_angle
