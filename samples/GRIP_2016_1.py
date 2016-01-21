'''
Python implementation of the 2016 GRIP example from:http://wpilib.screenstepslive.com/s/4485/m/50711/l/481750-using-grip-for-the-2016-game

Running on a Raspberry Pi 2B:
- /proc/cpuinfo Revision a01041
- /proc/cpuinfo Max 900MHz
- Ubuntu 15.04/3.18.0-25-rpi2 (2015/07/05)
- PS3 Playstation Eye webcam
Including all OpenCV and NetworkTable processing this averages:
- 18 FPS with PS3 Playstation Eye (YUYV/SRGB 640x480@30)
- 8 FPS with generic Chinese webcam (YUYV/SRGB 640x480@30)
'''

from networktables import NetworkTable
import logging
logging.basicConfig(level=logging.DEBUG)
NetworkTable.setIPAddress("127.0.0.1")
NetworkTable.setClientMode()
NetworkTable.initialize()
cr = NetworkTable.getTable("SharkCV/myContoursReport")

import cv2
import numpy as np

def GRIP_2016_1(frame):
	# CV Resize
	step_0_0 = cv2.resize(frame, (320,240), interpolation=cv2.INTER_LINEAR)
	
	# HSL Threshold
	step_1_0 = cv2.cvtColor(step_0_0, cv2.COLOR_BGR2HLS)
	step_1_0 = cv2.inRange(step_1_0, np.array([63,55,168]), np.array([96,161,255]))
	
	# Find Contours
	contours, hierarchy = cv2.findContours(step_1_0, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)
	step_2_0 = []
	for cnt in contours:
		dict = {'area':0, 'width':0, 'centerX':0, 'centerY':0}
		dict['area'] = cv2.contourArea(cnt)
		if dict['area'] > 0:
			x, y, dict['width'], dict['height'] = cv2.boundingRect(cnt)
			dict['centerX'] = x + dict['width'] / 2
			dict['centerY'] = y + dict['height'] / 2
			step_2_0.append(dict)
			
	# Filter Contours
	step_3_0 = []
	for cnt in step_2_0:
		if cnt['area'] < 400:
			continue
		step_3_0.append(cnt)
		
	# Publish ContoursReport
	for idx, cnt in enumerate(step_3_0):
		table = cr.getSubTable(idx)
		table.putValue('area', area)
		table.putValue('width', width)
		table.putValue('height', height)
		table.putValue('centerX', centerX)
		table.putValue('centerY', centerY)