"""module implementing the OffsetWidget class"""

from PySide2 import QtCore, QtWidgets, QtGui

class OffsetWidget(QtWidgets.QWidget):

	def __init__(self, inc_step = 0.1, tracker = None):
		super().__init__()

		self.inc_step = inc_step
		self.tracker = tracker

		self.init_layout()

	def set_tracker(self, tracker):
		self.tracker = tracker

	def offset_update(self, alt, az):
		if (self.tracker != None):
			self.tracker.add_tracking_offset(alt*self.inc_step, az*self.inc_step)
	
	def offset_reset(self):
		if (self.tracker!=None):
			self.tracker.set_tracking_offset(0, 0)

	def init_layout(self):
		self.group_box = QtWidgets.QGroupBox()
		self.group_box.setTitle("Offset Control")
		
		self.gridLayout = QtWidgets.QGridLayout(self.group_box)
		self.gridLayout.setObjectName("gridLayout")

		self.AltIncButton = QtWidgets.QPushButton(self.group_box)
		self.AltIncButton.setObjectName("AltIncButton")
		self.gridLayout.addWidget(self.AltIncButton, 0, 1, 1, 1)
		self.AltIncButton.clicked.connect(lambda alt=1,az=0: self.offset_update(alt, az))

		self.AzIncButton = QtWidgets.QPushButton(self.group_box)
		self.AzIncButton.setObjectName("AzIncButton")
		self.gridLayout.addWidget(self.AzIncButton, 1, 2, 1, 1)
		self.AzIncButton.clicked.connect(lambda alt=0,az=1: self.offset_update(alt, az))				

		self.AltDecButton = QtWidgets.QPushButton(self.group_box)
		self.AltDecButton.setObjectName("AltDecButton")
		self.gridLayout.addWidget(self.AltDecButton, 2, 1, 1, 1)
		self.AltDecButton.clicked.connect(lambda alt=-1,az=0: self.offset_update(alt, az))		

		self.AzDecButton = QtWidgets.QPushButton(self.group_box)
		self.AzDecButton.setObjectName("AzDecButton")
		self.gridLayout.addWidget(self.AzDecButton, 1, 0, 1, 1)
		self.AzDecButton.clicked.connect(lambda alt=0,az=-1: self.offset_update(alt, az))

		self.ResetButton = QtWidgets.QPushButton(self.group_box)
		self.ResetButton.setObjectName("ResetButton")
		self.gridLayout.addWidget(self.ResetButton, 1, 1, 1, 1)
		self.ResetButton.clicked.connect(self.offset_reset)


		self.AltIncButton.setText("Alt +")
		self.AzIncButton.setText("Az +")
		self.AltDecButton.setText("Alt -")
		self.AzDecButton.setText("Az -")
		self.ResetButton.setText("Reset")

		self.vbox_layout = QtWidgets.QVBoxLayout()
		self.vbox_layout.addWidget(self.group_box)

		self.setLayout(self.vbox_layout)

if __name__=="__main__":
	

	app = QtWidgets.QApplication([])
	widget = OffsetWidget()
	#widget.resize(800,600)
	widget.show()

	app.exec_()
