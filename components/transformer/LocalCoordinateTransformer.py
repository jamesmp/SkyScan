""" Module to facilitate the transformation of coordinates
from any epsg space to horizon-relative local cartesian 
coordinates"""

import numpy as np
import pyproj as proj

class LocalCoordinateTransformer:
	""" Class to facilitate the transformation of coordinates
	from any epsg space to horizon-relative local cartesian 
	coordinates"""


	local_position = None
	local_basis = None

	#Target CRS for all transforms, EPSG 4978 cartesian geocentric
	cart_crs = proj.CRS.from_epsg(4978)
	#Intermediate CRS for basis calculation, EPSG 4979 WGS84 Lat/Long/ellipsoid height
	radial_crs = proj.CRS.from_epsg(4979)

	#Cached transform from epsg:4979 to epsg:4978 (wgs84 Lat/Long/h to wgs84 cartesian)
	rad_cart_transform = proj.Transformer.from_crs(radial_crs, cart_crs)

	def __init__(self, local_position=[0.0, 0.0, 0.0], space="epsg:4979"):
		self.set_local_position(local_position, space)

	def set_local_position(self, local_position, space="epsg:4979"):
		""" Function to set local observer position and basis. Space string
		must be a valid PROJ String, JSON string with PROJ parameters,
		CRS WKT string, or an authority string, e.g. epsg:4979 """

		src_crs = proj.CRS.from_string(space)
		transformer = proj.Transformer.from_crs(src_crs, self.radial_crs)

		#Transform from the source space to radial space
		radial_position = transformer.transform(local_position[0], local_position[1], local_position[2] if len(local_position)>2 else 0)
		radial_position = np.array(radial_position)
		print("New Radial Pos: " + str(radial_position))

		#Transform position to cartesian space
		cart_position = self.rad_cart_transform.transform(radial_position[0], radial_position[1], radial_position[2])
		cart_position = np.array(cart_position)
		print("New Cartesian Pos: " + str(cart_position))

		#Get vectors for basis ----------------------

		#Get north radial pos
		point_north_rad = np.array(radial_position) + np.array([1e-5, 0.0, 0.0])

		#Correct for north pole...
		if point_north_rad[0] > 90.0:
			point_north_rad[0] = 180.0 - point_north_rad[0]

			if point_north_rad[1] > 0:
				point_north_rad[1] -= 180.0
			else:
				point_north_rad[1] += 180.0

		#Get up radial pos
		point_up_rad = np.array(radial_position) + np.array([0.0, 0.0, 0.1])

		#Get points in cartesian space
		point_north = self.rad_cart_transform.transform(point_north_rad[0], point_north_rad[1], point_north_rad[2])
		point_north = np.array(point_north)

		point_up = self.rad_cart_transform.transform(point_up_rad[0], point_up_rad[1], point_up_rad[2])
		point_up = np.array(point_up)

		#Derive local horizon (ellipsoidal) basis vectors
		v_z = point_up - cart_position
		v_z /= np.linalg.norm(v_z)

		v_y = point_north - cart_position
		v_y = (v_y - np.dot(v_y, v_z) * v_z)
		v_y /= np.linalg.norm(v_y)
		
		v_x = np.cross(v_y, v_z)

		print("Local basis (x, y, z): " + str([v_x, v_y, v_z]))

		self.local_basis = np.array([v_x, v_y, v_z])
		self.local_position = np.array(cart_position)

	def transform_to_local(self, pos, space="epsg:4979"):
		src_pos = np.array(pos)

		if len(src_pos)!=3:
			print("SRC POS DOES NOT HAVE A HEIGHT!")

		if space!="epsg:4979":
			src_crs = proj.CRS.from_string(space)
			transformer = proj.Transformer.from_crs(src_crs, self.radial_crs)

			src_pos = transformer.transform(src_pos[0], src_pos[1], src_pos[2] if len(src_pos)>2 else 0.0)

			print("Src pos transformed to WGS84: " + str(src_pos))

		cart_pos = self.rad_cart_transform.transform(src_pos[0], src_pos[1], src_pos[2])

		v_pos = self.local_basis.dot(cart_pos - self.local_position)

		return v_pos
		
if __name__=="__main__":
	trans = LocalCoordinateTransformer(local_position=[83934.30, 5382.06, 0.0], space="epsg:27700")

	local = trans.transform_to_local([87937.79, 8535.39, 2.0], space="epsg:27700")
	print(local)

	print(np.linalg.norm(local))