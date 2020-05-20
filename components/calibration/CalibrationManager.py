""" module containing the CalibrationManager class """

from ..solver.CalibrationSolver import CalibrationSolver
from ..solver.PointingSolver import PointingSolver
from ..solver.MountModel import MountModel
from ..tracking.Position import Position

import numpy as np
import copy

class CalibrationPoint:
    """ Class to hold calibration points """
    #Position of tracked object in local space
    local_pos = None

    #Driven angles for the position
    motor_angles = None

    #Point scope angle error
    reprojection_error = None

    #Trackable name
    object_name = None

class CalibrationManager:
    """ Class to handle the calibration process """

    #ObjectTracker instance to use to get calibration pairs
    object_tracker = None

    #CalibrationSolver instance
    calibration_solver = None

    #Current calibration parameters MountModel
    mount_model = None

    #List of calibration points used for solution
    point_list = None

    def __init__(self, object_tracker, mount_model = MountModel()):
        self.object_tracker = object_tracker
        self.mount_model = mount_model
        
        self.calibration_solver = CalibrationSolver()
        self.point_list = []

    def update_model(self, update_tracker=True):
        num_points = len(self.point_list)

        if num_points<=0:
            return -1.0

        pos_arr = np.zeros((num_points, 3))
        rots_arr = np.zeros((num_points, 2))

        idx = 0
        for cal_point in self.point_list:
            pos_arr[idx][0] = cal_point.local_pos[0]
            pos_arr[idx][1] = cal_point.local_pos[1]
            pos_arr[idx][2] = cal_point.local_pos[2]

            rots_arr[idx][0] = cal_point.motor_angles[0]
            rots_arr[idx][1] = cal_point.motor_angles[1]

            idx += 1

        old_model = self.mount_model.copy()

        params, result = self.calibration_solver.solve(self.mount_model, pos_arr, rots_arr)

        print("Calibration result:")
        print(result)

        if not result.success:
            self.mount_model = old_model
        else:
            self.mount_model.unpack_parameters(params)

            #Calculate reprojection error
            solver = PointingSolver(self.mount_model)

            for cal_point in self.point_list:
                scope_error = solver.scope_error(cal_point.motor_angles, cal_point.local_pos)

                cal_point.reprojection_error = scope_error

        if update_tracker:
            self.object_tracker.set_mount_model(self.mount_model.copy())

        return result.fun

    def send_model(self):
        self.object_tracker.set_mount_model(self.mount_model.copy())

    def reset_model(self):
        self.mount_model = MountModel()

    def get_model(self):
        if (self.mount_model==None):
            return None

        return self.mount_model.copy()

    def set_model(self, model):
        self.mount_model = model.copy()

    def delete_point(self, index, update_tracker=True):
        del self.point_list[index]

        self.update_model(update_tracker)

    def get_point_list(self):
        return copy.deepcopy(self.point_list)

    def capture_point(self):
        if (not self.object_tracker.is_tracking()):
            print("didn't capture, not tracking object")
            return

        state = self.object_tracker.get_state()
        object_name = self.object_tracker.get_tracked_object().get_name()

        if state.local_pos.pos_type!=Position.TYPE_CARTESIAN:
            raise RuntimeError("Position supplied to calibrator must be cartesian")

        cal_point = CalibrationPoint()
        cal_point.local_pos = (state.local_pos.x, state.local_pos.y, state.local_pos.z)
        cal_point.motor_angles = (state.alt, state.az)
        cal_point.object_name = object_name

        self.point_list.append(cal_point)

