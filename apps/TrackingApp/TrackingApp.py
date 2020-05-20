from PySide2 import QtCore, QtWidgets, QtGui
from ..TrackingApp.widgets.TrackingStatusWidget import TrackingStatusWidget
from ..TrackingApp.widgets.PlaneChooserWidget import PlaneChooserWidget
from ..TrackingApp.widgets.OffsetWidget import OffsetWidget
from ..TrackingApp.widgets.CalibrationWidget import CalibrationWidget

from ...components.aircraft.Dump1090Parser import Dump1090Parser
from ...components.aircraft.AircraftManager import AircraftManager
from ...components.tracking.ObjectTracker import ObjectTracker
from ...components.aircraft.TrackableAircraft import TrackableAircraft
from ...components.transformer.LocalCoordinateTransformer import LocalCoordinateTransformer
from ...components.interface.WebScope import WebScope
from ...components.calibration.CalibrationManager import CalibrationManager
from ...components.solver.MountModel import MountModel

from ...components.celestial import AlpacaServer
from ...components.celestial.TrackableCelestial import TrackableCelestial


import threading
import time
import json
import os
import logging

class TrackingApp(QtWidgets.QMainWindow):
	def __init__(self):
		super().__init__()

		self.load_config()

		self.init_layout()
		self.setWindowTitle("Aircraft Tracker")

		self.init_control()

	def load_config(self):
		config = None
		save_config = False

		if (os.path.isfile("config.json")):
			try:
				with open("config.json", "r") as file:
					config = json.load(file)
			except json.JSONDecodeError as err:
				logging.error("Config file parsing failed with error: {0}".format(err))
				config = None
			except OSError as err:
				logging.error("Config file loading failed with error: {0}".format(err))
				config = None
		else:
			save_config = True

		if (config==None):
			config = {
				"location": (0.0, 0.0, 0.0)
			}

		if save_config:
			self.save_config(config)
		
		self.config = config

	def save_config(self, config=None):
		if config==None:
			config = self.config

		try:
			with open("config.json", "w") as file:
				json.dump(config, file)
		except OSError as err:
			logging.warning("Failed to write config file to disk, error: {0}".format(err))

	@QtCore.Slot()
	def tracking_loop(self):
		#run tracker
		self.tracker.run()

		#update tracking display
		self.tracking_widget.update()

	@QtCore.Slot(str)
	def plane_select(self, icao_address):
		if (icao_address!=None and len(icao_address) > 0):
			trackable = TrackableAircraft(self.manager, icao_address)
			self.tracker.set_tracked_object(trackable)
		else:
			self.tracker.set_tracked_object(None)

	@QtCore.Slot()
	def alpaca_select(self):
		trackable = TrackableCelestial(self.alpaca_server)
		self.tracker.set_tracked_object(trackable)

	@QtCore.Slot()
	def alpaca_deselect(self):
		self.tracker.set_tracked_object(None)

	def init_control(self):
		self.parser = Dump1090Parser("127.0.0.1", 30003)
		self.manager = AircraftManager(self.parser)

		self.manager_thread = threading.Thread(target=self.manager.enter_update_loop, daemon=True)
		self.manager_thread.start()

		self.transformer = LocalCoordinateTransformer(self.config["location"])
		self.driver = WebScope("http://127.0.0.1:5000/api/v1/telescope/0")
		self.tracker = ObjectTracker(self.transformer, self.driver)

		self.alpaca_server = AlpacaServer

		self.calibration_manager = CalibrationManager(self.tracker)

		self.tracking_widget.set_object_tracker(self.tracker)
		self.chooser_widget.set_aircraft_manager(self.manager)
		self.chooser_widget.plane_selected_siganl.connect(self.plane_select)
		self.offset_widget.set_tracker(self.tracker)
		self.calibration_widget.set_calibration_manager(self.calibration_manager)

		self.alpaca_server.start_server()

		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.tracking_loop)
		self.timer.start(200)

	def init_layout(self):
		self.tracking_widget = TrackingStatusWidget()
		self.chooser_widget = PlaneChooserWidget()
		self.offset_widget = OffsetWidget()
		self.calibration_widget = CalibrationWidget()

		self.hbox_layout = QtWidgets.QHBoxLayout()
		self.hbox_layout.addWidget(self.tracking_widget)
		self.hbox_layout.addWidget(self.chooser_widget)
		self.hbox_layout.addWidget(self.offset_widget)
		self.hbox_layout.addWidget(self.calibration_widget)

		self.central_widget = QtWidgets.QWidget()
		self.central_widget.setLayout(self.hbox_layout)

		#Menu
		self.menu_bar = QtWidgets.QMenuBar(self)

		#File menu
		self.file_menu = self.menu_bar.addMenu("File")

		self.save_cal_model_action = QtWidgets.QAction(text="Save Cal Model", parent=self)
		self.save_cal_model_action.triggered.connect(lambda :self.save_model("cal"))
		self.file_menu.addAction(self.save_cal_model_action)

		self.load_cal_model_action = QtWidgets.QAction(text="Load Cal Model", parent=self)
		self.load_cal_model_action.triggered.connect(lambda :self.load_model("cal"))
		self.file_menu.addAction(self.load_cal_model_action)

		self.save_tracking_model_action = QtWidgets.QAction(text="Save Tracking Model", parent=self)
		self.save_tracking_model_action.triggered.connect(lambda :self.save_model("track"))
		self.file_menu.addAction(self.save_tracking_model_action)

		self.load_tracking_model_action = QtWidgets.QAction(text="Load Tracking Model", parent=self)
		self.load_tracking_model_action.triggered.connect(lambda :self.load_model("track"))
		self.file_menu.addAction(self.load_tracking_model_action)

		#Action Menu
		self.action_menu = self.menu_bar.addMenu("Actions")

		self.clear_planes_action = QtWidgets.QAction(text="Clear Planes", parent=self)
		self.clear_planes_action.triggered.connect(self.clear_planes)
		self.action_menu.addAction(self.clear_planes_action)

		self.track_alpaca_action = QtWidgets.QAction(text="Track with Alpaca", parent=self)
		self.track_alpaca_action.triggered.connect(self.alpaca_select)
		self.action_menu.addAction(self.track_alpaca_action)

		self.untrack_alpaca_action = QtWidgets.QAction(text="Stop tracking with Alpaca", parent=self)
		self.untrack_alpaca_action.triggered.connect(self.alpaca_deselect)
		self.action_menu.addAction(self.untrack_alpaca_action)

		self.setMenuBar(self.menu_bar)

		self.setCentralWidget(self.central_widget)
		print("Set layout")

	def clear_planes(self):
		""" callback to empty the plane manger list """
		self.tracker.set_tracked_object(None)
		self.manager.clear_plane_list()
		self.chooser_widget.reload_planes()

	def save_model(self, model_type):
		model = None

		if model_type=="cal":
			model = self.calibration_manager.get_model()
		else:
			model = self.tracker.get_model()

		filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, filter="*.json")

		if (len(filename)==0):
			return

		model.save_to_file(filename)

	def load_model(self, model_type):
		model = MountModel()

		filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, filter="*.json")

		if (len(filename)==0):
			return

		model.load_from_file(filename)

		if model_type=="cal":
			self.calibration_manager.set_model(model)
			self.calibration_widget.set_calibration_data()
		else:
			self.tracker.set_mount_model(model)

if __name__=="__main__":
	
	app = QtWidgets.QApplication([])
	widget = TrackingApp()
	
	widget.show()
	app.exec_()

	widget.manager.stop_update_loop()
	time.sleep(1)

	exit()
