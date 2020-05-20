"""module implementing the CalibrationWidget class"""

from PySide2 import QtCore, QtWidgets, QtGui

class CalibrationWidget(QtWidgets.QWidget):

	def __init__(self, calibration_manager=None):
		super().__init__()

		self.init_layout()

		self.set_calibration_manager(calibration_manager)
		self.set_status("Idle")
		self.list_selection_changed()

		self.list_widget.itemSelectionChanged.connect(self.list_selection_changed)
		self.add_point_button.clicked.connect(self.add_point)
		self.remove_point_button.clicked.connect(self.remove_point)
		self.send_model_button.clicked.connect(self.send_calibration_model)
		self.reset_model_button.clicked.connect(self.reset_calibration_model)

	def set_calibration_manager(self, calibration_manager):
		""" Sets the calibration manager and updates UI """
		self.calibration_manager = calibration_manager

		self.set_calibration_data()
		self.update_point_list()

	def reset_calibration_model(self):
		""" Calibration model reset button callback"""
		if (self.calibration_manager!=None):
			self.calibration_manager.reset_model()

			self.set_calibration_data()

	def send_calibration_model(self):
		""" Calibration model send button callback"""
		if (self.calibration_manager!=None):
			self.calibration_manager.send_model()

	def add_point(self):
		""" Calibration point add button callback"""
		if (self.calibration_manager!=None):
			self.calibration_manager.capture_point()

			avg_err = self.calibration_manager.update_model(update_tracker=False)
			self.set_status("Solver error: " + str(avg_err))

			self.update_point_list()
			self.set_calibration_data()

	def list_selection_changed(self):
		""" Calibration point list selection callback"""
		selection = self.list_widget.selectedItems()
		
		self.remove_point_button.setEnabled(len(selection) > 0)

	def remove_point(self):
		""" Calibration point removal button callback"""
		selection = self.list_widget.selectedItems()[0]
		index = selection.data(QtCore.Qt.UserRole)

		print(index)
		self.calibration_manager.delete_point(index)

		self.update_point_list()
		self.set_calibration_data()

	def update_point_list(self):
		""" re-fetch point list from calibration manager and update UI"""
		if (self.calibration_manager!=None):

			self.list_widget.clear()

			point_list = self.calibration_manager.get_point_list()

			index = 0
			for cal_point in point_list:
				point_text = "{index:d}: {p.object_name:s} - {p.reprojection_error:.4f}".format(index=index, p=cal_point)
				list_item = QtWidgets.QListWidgetItem(point_text, view=self.list_widget)

				list_item.setData(QtCore.Qt.UserRole, index)

				index += 1

	def set_status(self, status):
		self.status_label.setText(status)

	def set_calibration_data(self):
		""" update motionmodel data display """
		cal_rots = (0.0, 0.0, 0.0)
		cal_dec_roll = 0.0
		cal_dec_offset = 0.0
		cal_scope_yaw = 0.0

		if self.calibration_manager!=None:
			model = self.calibration_manager.get_model()

			if model!=None:
				cal_rots = (model.az_rot_x, model.az_rot_y, model.az_rot_z)
				cal_dec_roll = model.dec_roll
				cal_dec_offset = model.dec_offset
				cal_scope_yaw = model.scope_yaw

		self.az_rots_value.setText("{:.4f}, {:.4f}, {:.4f}".format(cal_rots[0], cal_rots[1], cal_rots[2]))
		self.dec_roll_value.setText("{:.4f}".format(cal_dec_roll))
		self.dec_offset_value.setText("{:.4f}".format(cal_dec_offset))
		self.scope_yaw_value.setText("{:.4f}".format(cal_scope_yaw))

	def init_layout(self):

		self.verticalLayout = QtWidgets.QVBoxLayout()
		self.verticalLayout.setObjectName("verticalLayout")
		self.group_box = QtWidgets.QGroupBox(self)
		self.group_box.setObjectName("group_box")

		self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.group_box)
		self.verticalLayout_2.setObjectName("verticalLayout_2")

		self.widget = QtWidgets.QWidget(self.group_box)
		self.widget.setObjectName("widget")
		self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
		self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
		self.horizontalLayout.setObjectName("horizontalLayout")

		self.list_widget = QtWidgets.QListWidget(self.widget)
		self.list_widget.setObjectName("list_widget")
		self.horizontalLayout.addWidget(self.list_widget)

		self.widget_2 = QtWidgets.QWidget(self.widget)
		self.widget_2.setObjectName("widget_2")
		self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget_2)
		self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
		self.verticalLayout_3.setObjectName("verticalLayout_3")

		#Buttons
		self.add_point_button = QtWidgets.QPushButton(self.widget_2)
		self.add_point_button.setObjectName("add_point_button")
		self.verticalLayout_3.addWidget(self.add_point_button)

		self.remove_point_button = QtWidgets.QPushButton(self.widget_2)
		self.remove_point_button.setObjectName("remove_point_button")
		self.verticalLayout_3.addWidget(self.remove_point_button)

		self.send_model_button = QtWidgets.QPushButton(self.widget_2)
		self.send_model_button.setObjectName("send_model_button")
		self.verticalLayout_3.addWidget(self.send_model_button)

		self.reset_model_button = QtWidgets.QPushButton(self.widget_2)
		self.reset_model_button.setObjectName("reset_model_button")
		self.verticalLayout_3.addWidget(self.reset_model_button)

		self.horizontalLayout.addWidget(self.widget_2)
		self.verticalLayout_2.addWidget(self.widget)

		#Status form
		self.status_form_widget = QtWidgets.QWidget()
		self.horizontalLayout.addWidget(self.status_form_widget)
		self.form_layout = QtWidgets.QFormLayout()
		self.form_layout.setVerticalSpacing(10)
		self.status_form_widget.setLayout(self.form_layout)

		#Line 0: Az rots
		self.az_rots_title = QtWidgets.QLabel()
		self.az_rots_title.setText("Rx,Ry,Rz: ")
		self.form_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.az_rots_title)

		self.az_rots_value = QtWidgets.QLabel()
		self.az_rots_value.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
		self.form_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.az_rots_value)

		#Line 1: Dec roll
		self.dec_roll_title = QtWidgets.QLabel()
		self.dec_roll_title.setText("Dec roll: ")
		self.form_layout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.dec_roll_title)

		self.dec_roll_value = QtWidgets.QLabel()
		self.dec_roll_value.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
		self.form_layout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.dec_roll_value)

		#Line 2: Dec offset
		self.dec_offset_title = QtWidgets.QLabel()
		self.dec_offset_title.setText("Dec offset: ")
		self.form_layout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.dec_offset_title)

		self.dec_offset_value = QtWidgets.QLabel()
		self.dec_offset_value.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
		self.form_layout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.dec_offset_value)

		#Line 3: Scope Yaw
		self.scope_yaw_title = QtWidgets.QLabel()
		self.scope_yaw_title.setText("Scope Yaw: ")
		self.form_layout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.scope_yaw_title)

		self.scope_yaw_value = QtWidgets.QLabel()
		self.scope_yaw_value.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
		self.form_layout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.scope_yaw_value)

		#Status label
		self.status_label = QtWidgets.QLabel(self.group_box)
		self.status_label.setObjectName("status_label")
		self.verticalLayout_2.addWidget(self.status_label)

		self.verticalLayout.addWidget(self.group_box)

		self.group_box.setTitle("Calibration")
		self.add_point_button.setText("Add Point")
		self.remove_point_button.setText("Remove Point")
		self.send_model_button.setText("Send Model")
		self.reset_model_button.setText("Reset Model")
		self.status_label.setText("Status")

		self.setLayout(self.verticalLayout)

if __name__=="__main__":
	

	app = QtWidgets.QApplication([])
	widget = CalibrationWidget()
	#widget.resize(800,600)
	widget.show()

	app.exec_()
