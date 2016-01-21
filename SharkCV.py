#!/usr/bin/env python

import logging
import os
import sys
import time

import cv2


# Start logging
logging.basicConfig(
	level=logging.INFO,
	format='[%(asctime)s] [%(levelname).4s] [%(filename)s:%(lineno)03d]   %(message)s',
	datefmt='%H:%M:%S'
)
logging.debug('Starting %s', os.path.splitext(__file__)[0])


# Dynamic import a Python algorithm file
modfile = None

# Look through command line arguments
if modfile is None:
	for i in range(1, len(sys.argv)):
		if os.path.exists(sys.argv[i]):
			modfile = sys.argv[i]
			break
		elif os.path.exists(sys.argv[i]+'.py'):
			modfile = sys.argv[i]+'.py'
			break

# Look through current folder and all subfolders
if modfile is None:
	for root, dirs, files in os.walk(os.path.dirname(os.path.realpath(__file__))):
		for file in files:
			file = os.path.join(root, file)
			if file.endswith('.py') and not os.path.samefile(file, __file__):
				modfile = file
				break
		if not modfile is None:
			break

	dir = os.path.dirname(os.path.realpath(__file__))
	for file in os.listdir(dir):
		if file.endswith('.py') and not os.path.samefile(file, __file__):
			modfile = file
			break

# Import the Python file
if not modfile is None:
	logging.info('Found module: %s', os.path.relpath(modfile))
	modfile = os.path.relpath(modfile)
	logging.info('Importing module: %s', modfile)
	# Add module's directory to Python's path
	moddir = os.path.dirname(os.path.abspath(modfile))
	if not moddir in sys.path:
		sys.path.insert(0, moddir)
	# Import the module's basename
	modname = os.path.splitext(os.path.basename(modfile))[0]
	try:
		module = __import__(modname)
		module = getattr(module, modname)
	except Exception, e:
		logging.error('Import failed: %s', str(e))
		sys.exit(1)
else:
	logging.info('No module to load')
	sys.exit(1)


# Main image loop
logging.debug('Opening webcam')
while True:
	# Open first available camera
	cap = cv2.VideoCapture(-1)
	if cap.isOpened():
		logging.info('Opened webcam @ %.fx%.f', cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH), cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))

	# Set up FPS list and iterator
	times = [0] * 25
	time_idx = 0
	start = time.time()

	# Read webcam frames while possible
	while cap.isOpened():
		ret, frame = cap.read()
		if not ret:
			logging.warning('Failed to read webcam frame')
			break

		# Execute module file
		try:
			module(frame)
		except Exception, e:
			logging.error('Module exception: %s', str(e))
			sys.exit(1)

		# Compute FPS information
		end = time.time()
		times[time_idx] = end - start
		time_idx += 1
		if time_idx >= len(times):
			logging.info('Average FPS: %.1f', 1/(sum(times)/len(times)))
			time_idx = 0
		if time_idx > 0 and time_idx % 5 == 0:
			logging.debug('Average FPS: %.1f', 1/(sum(times)/len(times)))
		start = end

	cap.release()
	time.sleep(0.05)
