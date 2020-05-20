""" PointingSolver Module,
	Given a calibrated Mountmodel, and point inputs, can solve 
	for pointing angles
"""

import numpy as np
from scipy.optimize import minimize
import math

class PointingSolver:
	""" Class to calculate pointing angles given a target
	point and a calibrated MountModel
	"""

	def __init__(self, model):
		self.model = model

	def set_model(self, model):
		self.model = model

	def solve(self, pos, guess = None):
		""" For an object at position pos, solves the 
		MountModel to produce the pointing angles [Alt, Az]
		"""

		#Guess where point would be if there were no alignment errors
		if guess==None:
			base_length = np.sqrt(pos[0]*pos[0] + pos[1]*pos[1])

			#Calculate local alt/az of point, including the stepper home
			#positions
			true_Alt = np.arctan(pos[2]/base_length)*180.0 / np.pi - self.model.dec_offset
			true_Az = -np.arctan2(pos[1], pos[0])*180.0 / np.pi - self.model.az_rot_z + 90.0

			guess = np.array([true_Alt, true_Az])

			#print("Guess is " + str(guess))

		res = minimize(fun=PointingSolver.err_func,
		         x0=guess, 
			     args=(self.model, pos), 
				 #jac=PointingSolver.diff_func,
				 bounds=[(None, None), (None, None)],

				 method="L-BFGS-B",
				 #method="Nelder-Mead",
				 options={
					 "gtol": 1e-10
					 #"xatol": 1e-9,
					 #"fatol": 1e-9
				 }
		)

		scope_error = self.scope_error(res.x, pos)
		result_angles = np.mod(res.x, 360.0)

		if res.success:
			return result_angles, res, scope_error
		else:
			print("Solving for Alt, Az failed with message: ")
			print(res.message)

			return result_angles, res, scope_error

	def get_point_altaz(self, pos):
		result_angles, res, scope_error = self.solve(pos)

		return result_angles[0], result_angles[1]

	@staticmethod
	def err_func(rots, model, pos):
		scope_pos = model.transform(pos, rots)

		# Object should be along y axis, so x and z should be 0
		#print("pos in scope " + str(scope_pos))

		v_len = np.linalg.norm(scope_pos)

		#print("angular error: " + str(np.arccos(scope_pos[1]/v_len) * 180.0 / np.pi))

		err = 1.0 - (scope_pos[1] / v_len)
		return err*10.0

	def scope_error(self, rots, pos):
		scope_pos = self.model.transform(pos, rots)

		v_len = np.linalg.norm(scope_pos)

		return np.arccos(scope_pos[1]/v_len) * 180.0 / np.pi

	def plot_error_surf(self, pos):
		import matplotlib.pyplot as plt
		from matplotlib import cm

		alt = np.linspace(-30.0, 00.0, 60)
		az = np.linspace(-180.0, 180.0, 60)

		alts, azs = np.meshgrid(alt, az)
		errs = np.zeros(alts.shape)

		for i in range(alts.shape[0]):
			for j in range(alts.shape[1]):
				errs[i][j] = np.clip(np.power(PointingSolver.err_func(np.array([alts[i][j], azs[i][j]]), self.model, pos), 0.3), 0, 0.6)

		base_length = np.sqrt(pos[0]*pos[0] + pos[1]*pos[1])

		true_Alt = np.arctan(pos[2]/base_length)*180.0 / np.pi - self.model.dec_offset
		true_Az = -np.arctan2(pos[1], pos[0])*180.0 / np.pi - self.model.az_rot_z + 90.0

		guess = np.array([true_Alt, true_Az])
		guess_err = PointingSolver.err_func(guess, self.model, pos)

		res, result, scope_error = self.solve(pos)
		print(result)

		fig = plt.figure()
		ax = fig.gca(projection="3d")
		ax.set_xlabel("Alt")
		ax.set_ylabel("Az")

		ax.plot_surface(alts, azs, errs, cmap=cm.coolwarm, linewidth=0)
		#ax.plot([true_Alt], [true_Az], [np.power(guess_err, 0.3)], c="k", zorder=1, marker="X", markersize=10)
		ax.plot([res[0]], [res[1]], [np.power(result.fun, 0.3)], c="r", zorder=1, marker="X", markersize=10)
		plt.show()

	@staticmethod
	def diff_func(rots, model, pos):
		base_err = PointingSolver.err_func(rots, model, pos)

		step = 0.1

		dAlt = (PointingSolver.err_func(rots + np.array([step, 0]), model, pos) - base_err) / step
		dAz  = (PointingSolver.err_func(rots + np.array([0, step]), model, pos) - base_err) / step

		print("derr/dAlt = " + str(dAlt) + " derr/dAz = " + str(dAz))
		return np.array([dAlt, dAz])

if __name__ == "__main__":
	from MountModel import MountModel

	model = MountModel()
	model.az_rot_x = 6.118007728128404
	model.az_rot_y = -2.8851025876976557
	model.az_rot_z = -86.42961646591627

	model.dec_roll = 0.0
	model.dec_offset = 104.25137406825434
	model.scope_yaw = 10.574667799307793

	solver = PointingSolver(model)

	#result, res = solver.solve(np.array([0.3, 0.3, 0.4]))
	solver.plot_error_surf(np.array([ -0.08065829,  0.03929962,  0.99596676]))

	#print(result)
	#print(res)