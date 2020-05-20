"""module implementing the PlaneChooserWidget class"""

from PySide2 import QtCore, QtWidgets, QtGui

class PlaneChooserWidget(QtWidgets.QWidget):

    #Reference to the plane source
    aircraft_manager = None

    #dictionary of planes
    planes = None

    #Signal that a plane has been selected
    plane_selected_siganl = QtCore.Signal(str)

    def __init__(self, aircraft_manager=None, callback=None):
        super().__init__()

        self.aircraft_manager = aircraft_manager
        self.planes = {}

        self.init_layout()
        self.reload_planes()

        self.callback = callback

        self.plane_list_widget.itemSelectionChanged.connect(self.list_selection_changed)
        self.select_button.clicked.connect(self.select_plane)
        self.deselect_button.clicked.connect(self.deselect_plane)
        self.refresh_button.clicked.connect(self.reload_planes)

        #tst = QtWidgets.QPushButton(text="Clr")
        #tst.clicked.connect(self.clear_plane_list)
        #self.button_vbox.addWidget(tst)

    def set_aircraft_manager(self, aircraft_manager):
        self.aircraft_manager = aircraft_manager

    def set_callback(self, callback):
        self.callback = callback

    def clear_plane_list(self):
        self.planes = {}

        self.plane_list_widget.clear()

    def list_selection_changed(self):
        selection = self.plane_list_widget.selectedItems()
        
        self.select_button.setEnabled(len(selection) > 0)

    def select_plane(self):
        """ select plane button callback """
        selection = self.plane_list_widget.selectedItems()[0]
        
        self.plane_selected_siganl.emit(selection.data(QtCore.Qt.UserRole))
        #if (self.callback!=None):
            #self.callback(selection.text())

    def deselect_plane(self):
        """ deselect plane button callback"""
        self.plane_selected_siganl.emit(None)
        #if (self.callback!=None):
            #self.callback(None)
    
    def reload_planes(self):
        """ plane list reload button callback"""
        if (self.aircraft_manager!=None):
            self.planes = self.aircraft_manager.get_planes() #["85AC38", "83S7B2", "D728FA"]
        else:
            self.planes = {}

        self.plane_list_widget.clear()
        for icao_address, plane in self.planes.items():
            text = icao_address
            if plane.callsign!=None:
                text += " (" + plane.callsign + ")"

            item = QtWidgets.QListWidgetItem(text, view=self.plane_list_widget)
            item.setData(QtCore.Qt.UserRole, icao_address)

    def init_layout(self):
        self.top_layout = QtWidgets.QVBoxLayout()

        self.group_box = QtWidgets.QGroupBox()
        self.group_box.setTitle("Plane Chooser")
        self.top_layout.addWidget(self.group_box)

        self.hbox_layout = QtWidgets.QHBoxLayout()
        self.group_box.setLayout(self.hbox_layout)

        self.plane_list_widget = QtWidgets.QListWidget()
        self.plane_list_widget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.hbox_layout.addWidget(self.plane_list_widget)

        self.button_vbox = QtWidgets.QVBoxLayout()
        self.hbox_layout.addLayout(self.button_vbox)

        self.select_button = QtWidgets.QPushButton(text = "Select Active")
        self.select_button.setEnabled(False)
        self.button_vbox.addWidget(self.select_button)

        self.deselect_button = QtWidgets.QPushButton(text = "Deselect")
        self.button_vbox.addWidget(self.deselect_button)

        self.refresh_button = QtWidgets.QPushButton(text = "Refresh")
        self.button_vbox.addWidget(self.refresh_button)

        self.setLayout(self.top_layout)

if __name__=="__main__":
    from ....components.aircraft.Dump1090Parser import Dump1090Parser
    from ....components.aircraft.AircraftManager import AircraftManager
    import threading

    parser = Dump1090Parser("127.0.0.1",30003)
    manager = AircraftManager(parser)
    manager_thread = threading.Thread(target=manager.enter_update_loop)
    manager_thread.start()

    app = QtWidgets.QApplication([])



    widget = PlaneChooserWidget(manager, lambda icao_address: print(icao_address))
    #widget.resize(800,600)
    widget.show()

    app.exec_()

    manager.stop_update_loop()