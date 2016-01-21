# SharkCV
FRC-focused Python implementation of OpenCV and NetworkTables designed for a coprocessor.

### Installation
##### Raspberry Pi
To install all necessary dependencies run the following:
```
sudo apt-get install python-numpy python-opencv
sudo pip install pynetworktables
```

### Execution
To execute `SharkCV` run the following:
```
sudo python SharkCV.py [module.py]
```
Root access is required for `/dev/video*`.