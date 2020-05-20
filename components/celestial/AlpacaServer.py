""" Module containing AlpacaServer class """

from flask import Flask, Blueprint, request
import threading
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler("log.txt", "w"))

werkzeuglogger = logging.getLogger("werkzeug")
werkzeuglogger.addHandler(logging.FileHandler("server_log.txt", "w"))

def build_response(req, error_num = 0, error_message = ""):
	resp = {
		"ServerTransactionID": 0,
		"ErrorNumber": error_num,
		"ErrorMessage": error_message
	}

	try:
		resp["ClientTransactionID"] = req.form["ClientTransactionID"]
	except KeyError:
		resp["ClientTransactionID"] = 0

	return resp

def valfunc(f):

	def df(*args, **kwargs):
		resp = build_response(request)

		resp["Value"] = f(*args, **kwargs)

		logger.info("\"" + f.__name__ + "\": " + str(resp["Value"]))

		return resp

	df.__name__ = f.__name__

	return df

def respfunc(f):

	def df(*args, **kwargs):
		resp = build_response(request)

		return f(resp, *args, **kwargs)

	df.__name__ = f.__name__

	return df

#Variable lock
var_lock = threading.Lock()

# Variables
connected = False

latitude = 0.0
longitude = 0.0
elevation = 0.0

ra_apparent = 0.0
dec_apparent = 0.0


#Routes
albp = Blueprint("alpaca endpoint", __name__)

@albp.route("/telescope/<int:scope_id>/slewtoaltazasync", methods=["PUT"])
def telescope_slewtoaltaz(scope_id):
	alt = float(request.form["Altitude"])
	az = float(request.form["Azimuth"])

	return build_response(request)

@albp.route("/telescope/<int:scope_id>/slewtocoordinatesasync", methods=["PUT"])
def telescope_slewtocoordinatesasync(scope_id):
	ra = float(request.form["RightAscension"])
	dec = float(request.form["Declination"])

	print("SLEW to " + str((ra, dec)))
	global ra_apparent
	global dec_apparent

	with var_lock:
		ra_apparent = ra * 360.0 / 24.0
		dec_apparent = dec

	return build_response(request)

@albp.route("/telescope/<int:scope_id>/altaz", methods=["GET"])
def telescope_get_altaz(scope_id):
	resp = build_response(request)
	resp["Altitude"] = 0.0
	resp["Azimuth"] = 0.0

	return resp

@albp.route("/telescope/<int:scope_id>/altitude", methods=["GET"])
@valfunc
def telescope_get_altitude(scope_id):
	return 0.0

@albp.route("/telescope/<int:scope_id>/azimuth", methods=["GET"])
@valfunc
def telescope_get_azimuth(scope_id):
	return 0.0

@albp.route("/telescope/<int:scope_id>/slewing", methods=["GET"])
@valfunc
def telescope_get_slewing(scope_id):
	return False

@albp.route("/telescope/<int:scope_id>/abortslew", methods=["PUT"])
def telescope_abortslew(scope_id):
	resp = build_response(request)

	return resp

#Speed control
@albp.route("/telescope/<int:scope_id>/altrate", methods=["PUT"])
def telescope_altrate(scope_id):
	rate = float(request.form["AltitudeRate"])

	return build_response(request)

@albp.route("/telescope/<int:scope_id>/azrate", methods=["PUT"])
def telescope_azrate(scope_id):
	rate = float(request.form["AzimuthRate"])

	return build_response(request)

@albp.route("/telescope/<int:scope_id>/altazrate", methods=["PUT"])
def telescope_altazrate(scope_id):
	alt_rate = float(request.form["AltitudeRate"])
	az_rate = float(request.form["AzimuthRate"])

	return build_response(request)


#Boilerplate stuff
@albp.route("/telescope/<int:scope_id>/interfaceversion", methods=["GET"])
@valfunc
def telescope_interfaceversion(scope_id):
	return 1


@albp.route("/telescope/<int:scope_id>/connected", methods=["GET", "PUT"])
def telescope_connected(scope_id):
	resp = build_response(request)
	
	global connected
	if (request.method=="GET"):
		resp["Value"] = connected
	else:
		connected = request.form["Connected"]

	return resp

@albp.route("/telescope/<int:scope_id>/canslew", methods=["GET"])
@valfunc
def telescope_canslew(scope_id):
	return True

@albp.route("/telescope/<int:scope_id>/canslewasync", methods=["GET"])
@valfunc
def telescope_canslewasync(scope_id):
	return True

@albp.route("/telescope/<int:scope_id>/canslewaltaz", methods=["GET"])
@valfunc
def telescope_canslewaltaz(scope_id):
	return False

@albp.route("/telescope/<int:scope_id>/canslewaltazasync", methods=["GET"])
@valfunc
def telescope_canslewaltazasync(scope_id):
	return False

@albp.route("/telescope/<int:scope_id>/cansync", methods=["GET"])
@valfunc
def telescope_cansync(scope_id):
	return False

@albp.route("/telescope/<int:scope_id>/cansyncaltaz", methods=["GET"])
@valfunc
def telescope_cansycnaltaz(scope_id):
	return True

@albp.route("/telescope/<int:scope_id>/cansettracking", methods=["GET"])
@valfunc
def telescope_cansettracking(scope_id):
	return True

@albp.route("/telescope/<int:scope_id>/tracking", methods=["GET", "PUT"])
def telescope_tracking(scope_id):
	resp = build_response(request)

	if (request.method=="GET"):
		resp["Value"] = False

	return resp

@albp.route("/telescope/<int:scope_id>/atpark", methods=["GET"])
@valfunc
def telescope_atpark(scope_id):
	return True

@albp.route("/telescope/<int:scope_id>/declination", methods=["GET"])
@valfunc
def telescope_declination(scope_id):
	return dec_apparent

@albp.route("/telescope/<int:scope_id>/rightascension", methods=["GET"])
@valfunc
def telescope_rightascension(scope_id):
	return ra_apparent * 24.0 / 360.0

@albp.route("/telescope/<int:scope_id>/driverversion", methods=["GET"])
@valfunc
def telescope_driverversion(scope_id):
	return "1.0"

@albp.route("/telescope/<int:scope_id>/equatorialsystem", methods=["GET"])
@valfunc
def telescope_equatorialsystem(scope_id):
	return 1 #Amateur equatorial

@albp.route("/telescope/<int:scope_id>/canmoveaxis", methods=["GET"])
def telescope_canmoveaxis(scope_id):
	resp = build_response(request)
	axis = int(request.args["Axis"])

	#0=RA/Az, 1=Dec/Alt
	if (axis == 0 or axis==1):
		resp["Value"] = True
	else:
		resp["Value"] = False

	return resp

@albp.route("/telescope/<int:scope_id>/moveaxis", methods=["PUT"])
def telescope_moveaxis(scope_id):
	resp = build_response(request)
	axis = int(request.form["Axis"])
	rate = float(request.form["Rate"])

	#0=RA/Az, 1=Dec/Alt

	return resp

@albp.route("/telescope/<int:scope_id>/axisrates", methods=["GET"])
def telescope_axisrates(scope_id):
	resp = build_response(request)
	axis = request.args.get("axis")

	if axis==None:
		axis = request.args["Axis"]

	axis = int(axis)

	maximum = 10.0
	minimum = 0.0

	#0=RA/Az, 1=Dec/Alt

	resp["Value"] = [{"Maximum": maximum, "Minimum": minimum}]

	return resp

@albp.route("/telescope/<int:scope_id>/canpark", methods=["GET"])
@valfunc
def telescope_canpark(scope_id):
	return False

@albp.route("/telescope/<int:scope_id>/canpulseguide", methods=["GET"])
@valfunc
def telescope_canpulseguide(scope_id):
	return False

@albp.route("/telescope/<int:scope_id>/sitelatitude", methods=["GET", "PUT"])
def telescope_sitelatitude(scope_id):
	resp = build_response(request)

	global latitude
	if (request.method == "GET"):
		resp["Value"] = latitude
	elif (request.method == "PUT"):
		latitude = request.form["SiteLatitude"]
	
	return resp

@albp.route("/telescope/<int:scope_id>/sitelongitude", methods=["GET", "PUT"])
def telescope_sitelongitude(scope_id):
	resp = build_response(request)

	global longitude
	if (request.method == "GET"):
		resp["Value"] = longitude
	elif (request.method == "PUT"):
		longitude = request.form["SiteLongitude"]
	
	return resp

@albp.route("/telescope/<int:scope_id>/siteelevation", methods=["GET", "PUT"])
def telescope_siteelevation(scope_id):
	resp = build_response(request)

	global elevation
	if (request.method == "GET"):
		resp["Value"] = elevation
	elif (request.method == "PUT"):
		elevation = request.form["SiteElevation"]
	
	return resp


app = Flask(__name__)
app.register_blueprint(albp, url_prefix="/api/v1")


def start_server(host="0.0.0.0", port=5001):
	thread = threading.Thread(target=app.run, kwargs={"host": host, "port": port}, daemon=True)
	thread.start()

def get_ra_dec():
	ra = None
	dec = None

	with var_lock:
		ra = ra_apparent
		dec = dec_apparent

	return (ra, dec)