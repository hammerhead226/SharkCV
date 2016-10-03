'''
Python implementation of the 2016 GRIP example from: http://wpilib.screenstepslive.com/s/4485/m/50711/l/481750-using-grip-for-the-2016-game

Running on a Raspberry Pi 2B:
- /proc/cpuinfo Revision a01041
- /proc/cpuinfo Max 900MHz
- Ubuntu 15.04/3.18.0-25-rpi2 (2015/07/05)
Including all OpenCV and NetworkTable processing this averages:
- 23 FPS with PS3 PlayStation Eye (-vw 320 -vh 240)
- 23 FPS with Microsoft LifeCam HD 3000 (-vw 320 -vh 240)
- 8 FPS with generic Chinese webcam (-vw 320 -vh 240)
'''

import copy
import logging

from networktables import NetworkTable

logging.basicConfig(level=logging.DEBUG)
NetworkTable.setIPAddress("127.0.0.1")
NetworkTable.setClientMode()
NetworkTable.initialize()
cr = NetworkTable.getTable("SharkCV/myContoursReport")


def GRIP_2016_1(frame):
    # CV Resize
    frame.resize(320, 240)

    orig = copy.deepcopy(frame)

    # HSL Threshold
    frame.color_hls()
    mask = frame.threshold([63, 55, 168], [96, 161, 255])

    # Find Contours (happens when contours are referenced)

    # Filter Contours
    mask.contours_filter(area=(400, -1))

    # Publish ContoursReport
    for idx, cnt in enumerate(mask.contours):
        table = cr.getSubTable(str(idx))
        table.putValue('area', cnt.area)
        table.putValue('width', cnt.width)
        table.putValue('height', cnt.height)
        table.putValue('center_x', cnt.center_x)
        table.putValue('center_y', cnt.center_y)

    mask.contours_draw(orig)
    return orig
