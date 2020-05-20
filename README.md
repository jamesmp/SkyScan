# SkyScan (WIP)

A work in progress application to track aircraft, celestial objects, and satellites using motorised telescope mounts.

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