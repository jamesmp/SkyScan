""" CalibrationSolver Module,
	Given a Mountmodel, and point inputs, can solve 
	for calibration parameters
"""

import numpy as np
from scipy.optimize import minimize
import math

class CalibrationSolver:
	""" Class to calculate MountModel calibration 
	parameters from a set of point and pointing angle
	inputs
	"""

	def calc_average_offsets(self, pos_arr, rots_arr):
		offset_Alt = 0.0
		offset_Az = 0.0
		num_pts = 0

		for i in range(pos_arr.shape[0]):
			base_length = np.sqrt(pos_arr[i][0]*pos_arr[i][0] + pos_arr[i][1]*pos_arr[i][1])

			true_Alt = np.arctan(pos_arr[i][2]/base_length)*180.0 / np.pi
			true_Az = -np.arctan2(pos_arr[i][1], pos_arr[i][0])*180.0 / np.pi + 90.0

			actual_Alt = rots_arr[i][0]
			actual_Az = rots_arr[i][1]

			offset_Alt += np.mod(true_Alt-actual_Alt, 360.0)
			offset_Az += np.mod(true_Az-actual_Az, 360.0)

			num_pts += 1

		offset_Alt /= num_pts
		offset_Az /= num_pts

		return offset_Alt, offset_Az

	def solve(self, model, pos_arr, rots_arr, do_guess=True):
		""" For an object at position pos, solves the 
		MountModel to produce the pointing angles [Alt, Az]
		"""

		if pos_arr.shape[0] != rots_arr.shape[0]:
			print("Position array length not the same as rotations array!")
			return None, None

		if pos_arr.shape[1] != 3:
			print("Position array has wrong element size: " + str(pos_arr.shape[0]))
			return None, None

		if rots_arr.shape[1] != 2:
			print("Rotations array has wrong element size: " + str(rots_arr.shape[0]))
			return None, None

		if do_guess:
			avg_offset_Alt, avg_offset_Az = self.calc_average_offsets(pos_arr, rots_arr)

			#Stage 1, azimuth plane orientation
			model.az_rot_x = 0.0
			model.az_rot_y = 0.0

			#Most of the yaw offset is likely to come from Azimuth
			#drive offset
			model.az_rot_z = avg_offset_Az

			#Stage 3, declination roll
			model.dec_roll = 0.0

			#Stage 4, declination home offset
			#Likely to be most of the cause of altitude offset
			model.dec_offset = avg_offset_Alt

			#Stage 6, scope yaw from dec axis
			model.scope_yaw = 0.0

			print("Guess: " + str(model))

		model_params = model.pack_parameters()

		print("Initial params: " + str(model_params))
		

		res = minimize(fun=CalibrationSolver.err_func,
		         x0=model_params, 
			     args=(model, pos_arr, rots_arr), 
				 #jac=PointingSolver.diff_func,
				 #bounds=[(0, 90), (None, None)],

				 method="L-BFGS-B",
				 options={
					 "gtol": 1e-10,

				 }
		)

		if res.success:
			return res.x, res
		else:
			print("Calibration failed with message: ")
			print(res.message)

			return res.x, res

	@staticmethod
	def err_func(model_params, model, pos_arr, rots_arr):
		model.unpack_parameters(model_params)

		num_items = pos_arr.shape[0]
		err = 0.0

		#worst = 0.0

		for i in range(num_items):
			scope_pos = model.transform(pos_arr[i], rots_arr[i])

			v_len = np.linalg.norm(scope_pos)

			#ang = np.arccos(scope_pos[1]/v_len) * 180.0 / np.pi
			#if ang>worst:
			#	worst = ang

			err += 1.0 - (scope_pos[1] / v_len)

		err /= num_items
		#print("Worst: " + str(worst))

		return err*10.0