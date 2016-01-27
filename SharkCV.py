#!/usr/bin/env python

import argparse
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


# Parse arguments
parser = argparse.ArgumentParser(prog=__file__)
parser.add_argument('-i', metavar='file', dest='input_image', help='input image')
parser.add_argument('-wi', metavar='N', dest='webcam_index', help='webcam index (default: -1)', type=int, default=-1)
parser.add_argument('-ww', metavar='N', dest='webcam_width', help='webcam width', type=int)
parser.add_argument('-wh', metavar='N', dest='webcam_height', help='webcam height', type=int)
parser.add_argument('-wf', metavar='N', dest='webcam_fps', help='webcam fps', type=int)
parser.add_argument('module', nargs='?', help='python module file')
args = parser.parse_args()


# Dynamic import a Python algorithm file
modfile = None

# Look through command line arguments
if modfile is None and not args.module is None:
	if os.path.exists(args.module):
		modfile = args.module
	elif os.path.exists(args.module+'.py'):
		modfile = args.module+'.py'

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
	# Open webcam and set options
	cap = None
	if args.input_image is None:
		cap = cv2.VideoCapture(args.webcam_index)
		if cap.isOpened():
			if not args.webcam_width is None:
				cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, args.webcam_width)
			if not args.webcam_height is None:
				cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, args.webcam_height)
			if not args.webcam_fps is None:
				cap.set(cv2.cv.CV_CAP_PROP_FPS, args.webcam_fps)
			logging.info('Opened webcam @ %.fx%.f', cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH), cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))

	# Set up FPS list and iterator
	times = [0] * 25
	time_idx = 0
	start = time.time()

	# Continually process frames
	while True:
		# Get a frame to process
		frame = None

		# Read webcam frame
		if args.input_image is None and not cap is None and cap.isOpened():
			ret, frame = cap.read()
			if not ret:
				logging.warning('Failed to read webcam frame')
				break

		# Read input image
		if not args.input_image is None:
			if not os.path.exists(args.input_image):
				logging.error('Input image does not exist: %s', args.input_image)
				sys.exit(1)
			logging.info('Reading image: %s', args.input_image)
			frame = cv2.imread(args.input_image, cv2.IMREAD_COLOR)

		if frame is None:
			logging.error('Failed to get a frame')
			break


		# Execute module file
		try:
			module(frame)
		except Exception, e:
			logging.error('Module exception: %s', str(e))
			sys.exit(1)


		# Break loop if only one frame to process
		if not args.input_image is None:
			break

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

	# Release open webcam
	if not cap is None:
		cap.release()

	# Break loop if using input image
	if not args.input_image is None:
		break

	time.sleep(0.05)
