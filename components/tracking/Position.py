""" module to contain position class """
import math

dtr = math.pi / 180.0

class Position:
	TYPE_LATLONG = 0
	TYPE_ALTAZ = 1
	TYPE_CARTESIAN = 2

	alt = None
	az = None

	lat = None
	long = None
	height = None

	x = None
	y = None
	z = None

	pos_type = None

	def __init__(self, pos_type, alt=None, az=None, lat=None, long=None, height=None, x=None, y=None, z=None):
		self.pos_type = pos_type

		self.alt = alt
		self.az = az

		self.lat = lat
		self.long = long
		self.height = height

		self.x = x
		self.y = y
		self.z = z

	def as_tuple(self):
		if (self.pos_type == self.TYPE_ALTAZ):
			return (self.alt, self.az)
		elif (self.pos_type == self.TYPE_LATLONG):
			return (self.lat, self.long, self.height)
		elif (self.pos_type == self.TYPE_CARTESIAN):
			return (self.x, self.y, self.z)
		else:
			return (None, None, None)

	def to_cartesian(self):
		if (self.pos_type != self.TYPE_ALTAZ):
			raise RuntimeError("Can only convert altaz to cartesian")

		cart_pos = Position(Position.TYPE_CARTESIAN)

		cart_pos.z = math.sin(self.alt * dtr)
		base_length = math.cos(self.alt * dtr)

		cart_pos.y = base_length * math.cos(self.az * dtr)
		cart_pos.x = base_length * math.sin(self.az * dtr)

		return cart_pos

if __name__ == "__main__":
	test_pos = Position(Position.TYPE_ALTAZ, alt=45.0, az=270.0)
	print(test_pos.to_cartesian().as_tuple())