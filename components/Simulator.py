""" Module to simulate a calibration
routine
"""

from solver.PointingSolver import PointingSolver
from solver.CalibrationSolver import CalibrationSolver
from solver.MountModel import MountModel

import numpy as np

class MountModelDefaultGenerator:
	""" Class to hold the normal distribution properties
	of a MountModel, and provide a generate_model function
	to generate a model following these properties """

	#Stage 1, azimuth plane orientation
	az_rot_x_mean = 0.0
	az_rot_x_std = 5.0

	az_rot_y_mean = 0.0
	az_rot_y_std = 5.0

	az_rot_z_min = -180.0
	az_rot_z_max = 180.0

	#Stage 3, declination roll
	dec_roll_mean = 0.0
	dec_roll_std = 5.0

	#Stage 4, declination home offset
	dec_offset_min = -180.0
	dec_offset_max = 180.0

	#Stage 6, scope yaw from dec axis
	scope_yaw_mean = 0.0
	scope_yaw_std = 5.0

	def generate_model(self):
		model = MountModel()

		model.az_rot_x = np.random.normal(self.az_rot_x_mean, self.az_rot_x_std)
		model.az_rot_y = np.random.normal(self.az_rot_y_mean, self.az_rot_y_std)
		model.az_rot_z = np.random.uniform(self.az_rot_z_min, self.az_rot_z_max)

		model.dec_roll = np.random.normal(self.dec_roll_mean, self.dec_roll_std)

		model.dec_offset = np.random.uniform(self.dec_offset_min, self.dec_offset_max)

		model.scope_yaw = np.random.normal(self.scope_yaw_mean, self.scope_yaw_std)

		return model

class SimDefaultPointGenerator:
	""" Default class to generate calibration points
	for the simulator.
	"""

	def generate_points(self, solver, num_points=1, threshold=1e-6):
		points_arr = np.zeros((num_points, 3))
		rots_arr = np.zeros((num_points, 2))

		worst_error = -1.0

		aborted_points = 0
		i = 0
		while i < num_points:
			#Generate a random point
			alt = np.random.uniform(2.0, 85.0) * np.pi / 180.0
			az = np.random.uniform(-180.0, 180.0) * np.pi / 180.0

			vlen = np.random.uniform(0.4, 1000.0)

			points_arr[i][0] = np.cos(az)*np.cos(alt)*vlen
			points_arr[i][1] = np.sin(az)*np.cos(alt)*vlen
			points_arr[i][2] = np.sin(alt)*vlen

			#Solve for its rotations
			rots, result, scope_error = solver.solve(points_arr[i])

			if result.fun < threshold:
				rots_arr[i] = rots

				if result.fun > worst_error:
					worst_error = result.fun

				i+=1
			else:
				aborted_points += 1

		#print("Aborted " + str(aborted_points) + " points")
		print("Worst point gen error: " + str(worst_error))

		return points_arr, rots_arr


class Simulator:
	"""Class representing the simulator, contains
	the ground truth model, and can simulate calibration 
	of MountModels"""

	# Models for sim, true is the actual scope setup
	# used for generating Alt/Az values, calibration
	# is the taught model from the simulation data
	true_model = None
	calibration_model = None

	test_points = None
	test_rots = None

	pointing_solver = None
	calibration_solver = None

	model_gen = None
	point_gen = None

	def __init__(self, model_gen=MountModelDefaultGenerator(), point_gen=SimDefaultPointGenerator()):
		self.model_gen = model_gen
		self.point_gen = point_gen
		

	def generate_simulation(self, num_points=100):
		#setup ground truth model
		self.true_model = self.model_gen.generate_model()
		self.pointing_solver = PointingSolver(self.true_model)

		print(self.true_model)

		#Generate calibration points, with ground truth rotations
		self.test_points, self.test_rots = self.point_gen.generate_points(self.pointing_solver, num_points)

		#Setup model for calibration
		self.calibration_model = MountModel()
		self.calibration_solver = CalibrationSolver()

	def simulate_calibration(self):
		#Perform calibration
		num_points = self.test_points.shape[0]

		res_params, result = self.calibration_solver.solve(self.calibration_model, self.test_points, self.test_rots)

		#Log results
		print(result)

		true_params = self.true_model.pack_parameters()

		print("\n\n")
		print("Avg Error: " + str(result.fun))
		print("Solved: " + str(res_params))
		print("True: " + str(true_params))

	def evaluate_calibration(self, num_points=100):
		#Generate a new set of test cases
		test_points, test_rots = self.point_gen.generate_points(self.pointing_solver, num_points)

		#Create a pointing solver for the calibrated model
		calibrated_solver = PointingSolver(self.calibration_model)

		#Use the calibrated model to solve the points
		calibrated_rots = np.zeros((num_points, 2))
		scope_errors = np.zeros((num_points))

		for i in range(test_points.shape[0]):
			#Find the calibrated model drive angles for each point
			calibrated_rots[i], result, scope_error = calibrated_solver.solve(test_points[i])

			#Find the real world scope error of using the calibrated model
			# drive angles
			scope_errors[i] = self.pointing_solver.scope_error(calibrated_rots[i], test_points[i])

			if not result.success:
				print("ERROR when solving")
				print("point: " + str(test_points[i]))
				print("true rots: " + str(test_rots[i]))

				print(result)

		# Calculate error statistics
		mse = np.average(np.power(calibrated_rots-test_rots, 2))
		avg_scope_err = np.average(scope_errors)
		std_scope_err = np.std(scope_errors)
		worst_scope_err = np.max(scope_errors)

		print("Model MSE: " + str(mse))
		print("Avg scope err: " + str(avg_scope_err))
		print("Std of scope error: " + str(std_scope_err))
		print("Worst scope error: " + str(worst_scope_err))
		

if __name__=="__main__":
	sim = Simulator()

	sim.generate_simulation(num_points=5)
	print("\n\nSOLVING:\n")

	sim.simulate_calibration()
	sim.evaluate_calibration()