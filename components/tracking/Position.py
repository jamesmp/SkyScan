""" module to contain position class """

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