""" module to contain the TrackingStatusWidget class"""

from PySide2 import QtCore, QtWidgets, QtGui

import math

class TrackingStatusWidget(QtWidgets.QWidget):

    #Reference to the object tracker status to display
    object_tracker = None

    def __init__(self, object_tracker=None):
        super().__init__()

        self.object_tracker = object_tracker

        self.init_layout()
        self.update()

    def update(self):
        tracking_label = None
        tracking_latlong = [0.0, 0.0]
        tracking_altitude = 0.0
        tracking_altaz = [0.0, 0.0]
        tracking_distance = 0.0
        tracking_offset = [0.0, 0.0]

        if (self.object_tracker!=None):
            trackable = self.object_tracker.get_tracked_object()

            if (trackable!=None):
                pos = trackable.get_position()

                if (pos!=None):
                    last_motor_angle = self.object_tracker.get_last_motor_angle()

                    tracking_label = trackable.get_name()

                    if (pos.pos_type==pos.TYPE_LATLONG):
                        tracking_latlong = (pos.lat, pos.long)
                        tracking_altitude = pos.height

                    #Calculate object distance
                    local_pos = self.object_tracker.get_trackable_position()

                    if (local_pos.pos_type == local_pos.TYPE_CARTESIAN):
                        tracking_distance = math.sqrt(local_pos.x*local_pos.x + local_pos.y*local_pos.y + local_pos.z*local_pos.z)

                    tracking_altaz = last_motor_angle

            tracking_offset = self.object_tracker.get_tracking_offset()
            

        self.update_labels(tracking_label, tracking_latlong, tracking_altitude, tracking_altaz, tracking_distance, tracking_offset)

    def set_object_tracker(self, object_tracker):
        self.object_tracker = object_tracker

    def update_labels(self, label, latlong, altitude, altaz, distance, offset):
        if label==None:
            self.tracking_value.setText("<html><head/><body><p><span style=\" font-weight:600; color:#af2538;\">None</span></p></body></html>")
        else:
            self.tracking_value.setText("<html><head/><body><p><span style=\" font-weight:600; color:#30af25;\">" + label + "</span></p></body></html>")
        
        self.latlong_value.setText("{:.4f}, {:.4f}".format(latlong[0], latlong[1]))
        self.altitude_value.setText("{:.1f} m".format(altitude))
        self.altaz_value.setText("{:.4f}, {:.4f}".format(altaz[0], altaz[1]))
        self.distance_value.setText("{:.1f} m".format(distance))
        self.offset_value.setText("{:.4f}, {:.4f}".format(offset[0], offset[1]))

    def init_layout(self):
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.group_box = QtWidgets.QGroupBox()
        self.group_box.setObjectName("group_box")
        
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setVerticalSpacing(10)
        self.formLayout.setObjectName("formLayout")

        #Line 0
        self.tracking_title = QtWidgets.QLabel(self.group_box)
        self.tracking_title.setObjectName("tracking_title")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.tracking_title)

        self.tracking_value = QtWidgets.QLabel(self.group_box)
        self.tracking_value.setAlignment(QtCore.Qt.AlignCenter)
        self.tracking_value.setObjectName("tracking_value")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.tracking_value)

        #Line 1
        self.latlong_title = QtWidgets.QLabel(self.group_box)
        self.latlong_title.setObjectName("latlong_title")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.latlong_title)

        self.latlong_value = QtWidgets.QLabel(self.group_box)
        self.latlong_value.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.latlong_value.setObjectName("latlong_value")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.latlong_value)

        #Line 2
        self.altitude_title = QtWidgets.QLabel(self.group_box)
        self.altitude_title.setObjectName("altitude_title")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.altitude_title)

        self.altitude_value = QtWidgets.QLabel(self.group_box)
        self.altitude_value.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.altitude_value.setObjectName("altitude_value")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.altitude_value)

        #Line 3
        self.altaz_title = QtWidgets.QLabel(self.group_box)
        self.altaz_title.setObjectName("altaz_title")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.altaz_title)

        self.altaz_value = QtWidgets.QLabel(self.group_box)
        self.altaz_value.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.altaz_value.setObjectName("altaz_value")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.altaz_value)

        #Line 4
        self.distance_title = QtWidgets.QLabel(self.group_box)
        self.distance_title.setObjectName("distance_title")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.distance_title)

        self.distance_value = QtWidgets.QLabel(self.group_box)
        self.distance_value.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.distance_value.setObjectName("distance_value")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.distance_value)

        #Line 5
        self.offset_title = QtWidgets.QLabel(self.group_box)
        self.offset_title.setObjectName("offset_title")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.offset_title)

        self.offset_value = QtWidgets.QLabel(self.group_box)
        self.offset_value.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.offset_value.setObjectName("offset_value")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.offset_value)


        
        self.group_box.setLayout(self.formLayout)
        self.verticalLayout.addWidget(self.group_box)

        self.group_box.setTitle("Tracking Status")
        self.tracking_title.setText("Tracking: ")
        self.latlong_title.setText("Lat, Long: ")
        self.altitude_title.setText("Altitude: ")
        self.altaz_title.setText("Alt, Az: ")
        self.distance_title.setText("Distance: ")
        self.offset_title.setText("Offset: ")
        

if __name__=="__main__":
    app = QtWidgets.QApplication([])

    widget = TrackingStatusWidget()
    #widget.resize(800,600)
    widget.show()

    app.exec_()