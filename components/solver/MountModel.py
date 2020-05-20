""" Module implementing the model of the telescope mount """

from scipy.spatial.transform import Rotation
import json
import numpy as np
import logging

class MountModel:
	""" MountModel, retains calibration parameters, and methods
	for transforming coordinates into scope space """

	#Stage 1, azimuth plane orientation
	az_rot_x = 0.0
	az_rot_y = 0.0
	az_rot_z = 0.0

	#Stage 3, declination roll
	dec_roll = 0.0

	#Stage 4, declination home offset
	dec_offset = 0.0

	#Stage 6, scope yaw from dec axis
	scope_yaw = 0.0

	def __init__(self):
		self.load_default()

	def load_default(self):
		#Stage 1, azimuth plane orientation
		self.az_rot_x = 0.0
		self.az_rot_y = 0.0
		self.az_rot_z = 0.0

		#Stage 3, declination roll
		self.dec_roll = 0.0

		#Stage 4, declination home offset
		self.dec_offset = 0.0

		#Stage 6, scope yaw from dec axis
		self.scope_yaw = 0.0

	def copy(self):
		new_model = MountModel()
		
		params = self.pack_parameters()
		new_model.unpack_parameters(params)

		return new_model

	def transform(self, pos, rots):
		""" Take object position pos, and Mount rotation
		    rots, and output scope relative coordinates of the
			object

			pos = [x, y, z]
			rots = [Alt, Az]
		"""

		#Stage 1: Azimuth plane orientation matrix
		M1 = Rotation.from_euler("zxy", [self.az_rot_z, self.az_rot_x, self.az_rot_y], degrees=True).as_dcm()
		#Stage 2: Azimuth Rotation
		M2 = Rotation.from_euler("z", rots[1], degrees=True).as_dcm()
		#Stage 3: Declination roll
		M3 = Rotation.from_euler("y", self.dec_roll, degrees=True).as_dcm()
		#Stage 4+5: Declination Home + declination
		M54 = Rotation.from_euler("x", -(self.dec_offset + rots[0]), degrees=True).as_dcm()
		#Stage 6: Scope yaw
		M6 = Rotation.from_euler("z", self.scope_yaw, degrees=True).as_dcm()

		result = M6.dot(M54.dot(M3.dot(M2.dot(M1.dot(pos)))))

		return result

	def pack_parameters(self):
		return np.array([
			self.az_rot_x,
			self.az_rot_y,
			self.az_rot_z,
			self.dec_roll,
			self.dec_offset,
			self.scope_yaw
		])

	def unpack_parameters(self, params):
		self.az_rot_x = params[0]
		self.az_rot_y = params[1]
		self.az_rot_z = params[2]
		self.dec_roll = params[3]
		self.dec_offset = params[4]
		self.scope_yaw = params[5]

	def save_to_file(self, filename):
		data = {
			"az_rot_x": self.az_rot_x,
			"az_rot_y": self.az_rot_y,
			"az_rot_z": self.az_rot_z,
			"dec_roll": self.dec_roll,
			"dec_offset": self.dec_offset,
			"scope_yaw": self.scope_yaw
		}

		with open(filename, "w") as file:
			json.dump(data, file)


	def load_from_file(self, filename):
		data = None

		with open(filename, "r") as file:
			data = json.load(file)

		try:
			self.az_rot_x = data["az_rot_x"]
			self.az_rot_y = data["az_rot_y"]
			self.az_rot_z = data["az_rot_z"]
			self.dec_roll = data["dec_roll"]
			self.dec_offset = data["dec_offset"]
			self.scope_yaw = data["scope_yaw"]
		except KeyError:
			logging.warn("Loading MountModel from " + filename + " failed, incorrect data in file")
			self.load_default()


	def __str__(self):
		s = "MountModel\n"

		s += "    az_rot_x: " + str(self.az_rot_x) + "\n"
		s += "    az_rot_y: " + str(self.az_rot_y) + "\n"
		s += "    az_rot_z: " + str(self.az_rot_z) + "\n\n"

		s += "    dec_roll: "   + str(self.dec_roll)   + "\n"
		s += "    dec_offset: " + str(self.dec_offset) + "\n"
		s += "    scope_yaw: "  + str(self.scope_yaw)  + "\n"

		return s


if __name__ == "__main__":
	import numpy as np

	mod = MountModel()

	pos = np.array([1, 2, 3])
	rots = np.array([10, 0])

	print(mod.transform(pos, rots))