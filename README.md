# SharkCV
FRC-focused Python implementation of `OpenCV` and `NetworkTables` designed for a coprocessor.


## Linux Installation
To install all necessary dependencies run the following:
```
$ sudo apt-get install python-numpy python-opencv python-setuptools
$ sudo easy_install pip
$ sudo pip install pynetworktables
```

You may want to consider installing a mDNS client to interface with NetworkTables as well:
```
$ sudo apt-get install libnss-mdns
```


## Usage
#### Command-Line Arguments
To see a full list of command-line arguments run:
```
$ python SharkCV.py -h
```
There are arguments for various input types, output types, video input settings, and webcam settings.

#### Wired Webcam Input - Basic
```
$ python SharkCV.py [module.py]
```
- By default `SharkCV` will use the first webcam plugged in but you can specify it manually with an argument.
- Root access is sometimes required for webcams at `/dev/video*`.

#### Wired Webcam Input - Advanced
Here is an example that sets some video and webcam options:
```
$ python SharkCV.py -vw 320 -vh 240 -wb 0 -wh 127.5 [module.py]
```
- FPS improves dramatically when resolution is reduced. Setting webcam resolution with arguments (when supported by device) will yield faster processing than resizing with `OpenCV`.
- FPS can be greatly affected by webcam exposure time (and brightness if it affects the exposure).
- Webcams frequently do not obey settings from `OpenCV`/`V4L` (`-w*` arguments).

#### MJPG Input Stream
Thanks to [Mike Anderson](https://github.com/taichichuan) `mjpg-streamer` has been compiled for the roboRIO and it is possible to stream the same webcam to both Smart Dashboard and `SharkCV`. See below for MJPG output.
```
$ python SharkCV.py -im [url] [module.py]
```
- Video and webcam options will be ignored here, `mjpg-streamer input_uvc.so` must configured separately.
- Be mindful of the ports allowed by the FRC FMS when configuring `mjpg-streamer`.

#### File Output
`SharkCV` supports various output formats including images and videos.
```
$ python SharkCV.py -oi image.png [module.py]
$ python SharkCV.py -ov webcam.avi [module.py]
```
- Output filenames are processed through `datetime.strftime()` so they support [% date notation](https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior).
- File output is expensive and will cut your FPS significantly, especially on devices with poor throughput like the Raspberry Pi.

#### MJPG Output Stream
```
$ python SharkCV.py -oj [module.py]
```
- Browsing to your device's IP in a browser will serve an HTML page with the MJPG stream.
- HTTP server port is configurable but be mindful of the ports allowed by the FRC FMS.


## Module Construction
Here is an example methodology you can use to calibrate your `SharkCV` module/algorithm.

#### Input Setup
1. Decide what kind of input you will be using: local webcam, IP webcam, or static images.
2. Decide on what brightness/contrast/exposure/etc settings are best for your webcam. If tracking retro-reflective tape consider turning your brightness and exposure down for a darker image to give the tape more contrast.
3. If your image is upside-down (due to webcam mounting) you can use `rotate()` to correct it.

#### Threshold Calibration
1. Set up `SharkCV` to use your desired and have it output timestamped images. Example:
```
$ python SharkCV.py -oi "captures/%Y%m%d-%H%M%S-%f.png" [module.py]
```
2. Use an image editing such as GIMP to color-drop the item you want to track. Keep track of the min/max HLS/HSV values. Subtract some amount off the minimum and add some to the maximum to give yourself some variance tolerance.
3. Construct your module/algorithm using `threshold()` and `contours_draw()`. Using the same images you captured above run them through your module and have it output more timestamped images. Example:
```
$ python SharkCV.py -ii "captures/*.png" -oi "captures_processed/%Y%m%d-%H%M%S-%f.png" [module.py]
```
4. Check that the contours drawn on the images are what you want.

#### Other Operations
1. Consider using `resize()` before doing anything. `SharkCV` will process each frame much faster at lower resolutions. Power-of-two reductions seem to be the fastest.
2. Consider using `blur()`/`blur_gaussian()`/`blur_median()` first to smooth out your image (if necessary).
3. Consider using `dilate()`/`erode()` before finding contours. Warning, these operations can get expensive at large sizes or large number of iterations.
4. Consider using `contours_filter()`/`contours_sort()` before doing any kind of expensive operation on all contours.


## Credits
- [Thomas Clark](https://github.com/ThomasJClark) at [WPIRoboticsProjects](https://github.com/WPIRoboticsProjects) - author of `GRIP`, the inspiration for this project ([GitHub](https://github.com/WPIRoboticsProjects/GRIP)).
- [Mike Anderson](https://github.com/taichichuan) - `mjpg-streamer` for roboRIO ([Chief Delphi](http://www.chiefdelphi.com/forums/showthread.php?p=1460637)).
- [jacksonliam](https://github.com/jacksonliam) - `mjpg-streamer` fork for Rasperry Pi ([GitHub](https://github.com/jacksonliam/mjpg-streamer)).
- [Shih-Yuan Liu](https://github.com/shihyuan) - `mjpg-streamer` support for `OpenCV` ([GitHub](https://gist.github.com/shihyuan/4d834d429763e953a40c)).


## License
`SharkCV` is under GNU GPL v3 to ensure any derivatives are also open source.
