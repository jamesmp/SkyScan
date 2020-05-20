# SkyScan (WIP)

A work in progress application to track aircraft, celestial objects, and satellites using motorised telescope mounts.

[Short Demo](https://youtu.be/BJrJFTBbw6k) - A short Youtube video demonstrating a live camera feed of the tracking process,
The calibration process has not been performed for this video, as there are very few planes flying at the time of writing (Covid-19 2020)

## Operational Principle

The application allows the user to command any ASCOM Alpaca compatible telescope mount driver (Must currently support Alt/Az driving)
to track Aircraft (via [Dump1090](https://github.com/MalcolmRobb/dump1090)), Celestial objects (via [ASCOM Alpaca](https://ascom-standards.org/Developer/Alpaca.htm)), or Satellites (via [Orbitron](http://www.stoff.pl/) and a DDE bridge).

Internally, the application has a model of the current mount, which takes into account the following parameters:

* The orientation of the azimuth axis w.r.t. the local horizon
* The home positions of both azimuth and altitude motors
* The rotational offset of the declination axis away from perpendicular to the azimuth 
* The yaw of the capture device away from the declination axis

**Note**: The rotational offset of the declination axis, and the yaw of the capture device limit the possible range of motion of the mount

Regardless of the object type being tracked (except for satellites, which are WIP currently), the position reported is converted into
a local coordinate in cartesian space. This is performed by a class which generates the local coordinate basis in WGS84 cartesian space. From here the local vector to the object is passed to the pointing solver, which uses the object position, and the mount calibration model to solve for the Alt and Az drive angles for the scope.

These drive angles are then sent to the mount over an ASCOM Alpaca connection to any client supporting slewtoaltazasync.

### Tracking Aircraft

When tracking aircraft via a connection to [Dump1090](https://github.com/MalcolmRobb/dump1090), the software interprets location and 
velocity update messages, and incorporates these into an internal model for each aircraft. Several times a second, the software performs motion updates of all of the planes in its list, and forces position updates whenever new information becomes available.

A SDR device is essential for this part of the program.

### Tracking Celestial Bodies

The program exposes a partial implementation of the [ASCOM Alpaca API](https://ascom-standards.org/api/) on an endpoint, this can be commanded via any celestial software which supports ASCOM drivers, or ASCOM Alpaca explicitly.

### Tracking Satellites

This compenent is currently WIP and will not work correctly at this time. It requires an additional program I have created which I have not uploaded yet to communicate with [Orbitron](http://www.stoff.pl/) over its DDE connection.

## Getting Started

The project was developed on python 3.7.1, it has not been tested on earlier versions. The python module dependencies are
listed in the environment.yml file, which can be fed into anaconda to install all the packages you need to run the 
program.

### Prerequisites

* Python >=3.7.1 (Earlier versions untested, they may work)
* scipy >=1.4.1
* pyproj >=2.4.1
* proj-datumgrid-europe
* proj-datumgrid-world
* proj-datumgrid-north-america
* proj-datumgrid-oceania
* requests >=2.23.0
* flask >=1.1.1

### Installing

To setup the dev environment using anaconda, do the following

Create the new environment

```
conda env create -f environment.yml
```

Activate the environment

```
conda activate telescope
```

Run the test application from the root folder

```
python -m apps.TrackingApp.TrackingApp
```

## Built With

* [Pyproj](https://github.com/pyproj4/pyproj) - For Lat/Long/h to Cartesian coordinate transforms
* [SciPy](https://www.scipy.org/) - For coordinate transforms and calibration minimisation
* [Flask](https://palletsprojects.com/p/flask/) - Web framework for ASCOM Alpaca integration
* [PySide2](https://doc.qt.io/qtforpython/) - Official QT bindings for python for GUI
* [Requests](https://requests.readthedocs.io/en/master/) - For all basic web requests


## Authors

* **James Pearson** - [jamesmp](https://github.com/jamesmp)