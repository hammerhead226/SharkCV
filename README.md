# SharkCV
FRC-focused Python implementation of OpenCV and NetworkTables designed for a coprocessor.

## Installation
#### Debian / Ubuntu / Raspberry Pi
To install all necessary dependencies run the following:
```
sudo apt-get install python-numpy python-opencv
sudo pip install pynetworktables
```

## Usage
#### Basic Usage
To execute `SharkCV` run the following:
```
sudo python SharkCV.py [module.py]
```
Root access is required for `/dev/video*` (webcams).

#### Command-Line Options
To see a full list of command-line options run:
```
python SharkCV.py -h
```
There are options for various input file types, output file types, video input options, and webcam settings. Note: webcams frequently do not obey settings from `OpenCV`/`V4L`.

Advanced example:
```
sudo python SharkCV.py -iv 0 -vw 320 -vh 240 -ov webcam.avi samples/GRIP_2016_1.py
```
This will use webcam #0 at 320x240 resolution, process it using samples/GRIP_2016_1.py, and output the result to webcam.avi.

## License
`SharkCV` is under GNU GPL v3 to ensure any derivatives are also open source.

#### Libraries
- `OpenCV` is under BSD to require attribution and copyright inclusion.
- `Numpy` is under BSD to require attribution and copyright inclusion.
- `WPILib` is under BSD to require attribution and copyright inclusion.