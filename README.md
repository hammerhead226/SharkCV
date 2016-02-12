# SharkCV
FRC-focused Python implementation of `OpenCV` and `NetworkTables` designed for a coprocessor.


## Installation
To install all necessary dependencies run the following:
```
sudo apt-get install python-numpy python-opencv python-setuptools
sudo easy_install pip
sudo pip install pynetworktables
```


## Usage
#### Command-Line Arguments
To see a full list of command-line arguments run:
```
python SharkCV.py -h
```
There are arguments for various input file types, output file types, video input settings, and webcam settings.

#### Wired Webcam - Basic
By default `SharkCV` will use the first webcam plugged in but you can specify it manually with an argument.
```
sudo python SharkCV.py [module.py]
```
- Root access is required for `/dev/video*`.

#### Wired Webcam - Advanced
Here is an example that sets some video and webcam options:
```
sudo python SharkCV.py -vw 320 -vh 240 -wb 0 -wh 127.5 [module.py]
```
- FPS improves dramatically when resolution is reduced. Setting webcam resolution with arguments (when supported by device) will yield faster processing than resizing with `OpenCV`.
- Webcams frequently do not obey settings from `OpenCV`/`V4L` (`-w*` arguments).

#### MJPG Stream
Thanks to @taichichuan `mjpg-streamer` has been compiled for the roboRIO and it is possible to stream the same webcam to both Smart Dashboard and `SharkCV`.
```
python SharkCV.py -im [url] [module.py]
```
- Video and webcam options will be ignored here, `mjpg-streamer input_uvc.so` must configured separately.

#### File Output
`SharkCV` supports various output formats including images and videos.
```
sudo python SharkCV.py -ov webcam.avi [module.py]
```
- Output filenames are processed through `time.strftime()` so they support % date notation.
- File output is expensive and will cut your FPS significantly, especially on devices with poor throughput like the Raspberry Pi.


## Credits
- @ThomasJClark at @WPIRoboticsProjects - author of `GRIP`, the inspiration for this project (https://github.com/WPIRoboticsProjects/GRIP)
- @taichichuan - `mjpg-streamer` for roboRIO (http://www.chiefdelphi.com/forums/showthread.php?p=1460637)
- @jacksonliam - `mjpg-streamer` fork for Rasperry Pi (https://github.com/jacksonliam/mjpg-streamer)
- @shihyuan - `mjpg-streamer` support for `OpenCV` (https://gist.github.com/shihyuan/4d834d429763e953a40c)


## License
`SharkCV` is under GNU GPL v3 to ensure any derivatives are also open source.

#### Libraries
- `OpenCV` is under BSD to require attribution and copyright inclusion.
- `Numpy` is under BSD to require attribution and copyright inclusion.
- `WPILib` is under BSD to require attribution and copyright inclusion.