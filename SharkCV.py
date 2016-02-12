#!/usr/bin/env python

import argparse
import logging
import os
import sys
import time

import cv2
import numpy as np

import sharkcv


# Parse arguments
parser = argparse.ArgumentParser(prog=__file__)
group_input = parser.add_argument_group('input source')
group_input = group_input.add_mutually_exclusive_group()
group_input.add_argument('-ii', metavar='file', dest='input_image', help='input image')
group_input.add_argument('-iv', metavar='N', dest='input_video', help='input video/webcam (default: -1)', default=-1)
group_output = parser.add_argument_group('output file(s)')
group_output.add_argument('-oi', metavar='file', dest='output_image', help='output image')
group_output.add_argument('-ov', metavar='file', dest='output_video', help='output video')
group_video = parser.add_argument_group('video options')
group_video.add_argument('-vw', metavar='N', dest='video_width', help='video width', type=int)
group_video.add_argument('-vh', metavar='N', dest='video_height', help='video height', type=int)
group_video.add_argument('-vf', metavar='N', dest='video_fps', help='video fps (webcam default: 30.0)', type=float, default=30.0)
group_webcam = parser.add_argument_group('webcam options')
group_webcam.add_argument('-wb', metavar='[0-255]', dest='webcam_brightness', help='webcam brightness', type=float)
group_webcam.add_argument('-wc', metavar='[0-255]', dest='webcam_contrast', help='webcam contrast', type=float)
group_webcam.add_argument('-we', metavar='[0-255]', dest='webcam_exposure', help='webcam exposure', type=float)
group_webcam.add_argument('-wg', metavar='[0-255]', dest='webcam_gain', help='webcam gain', type=float)
group_webcam.add_argument('-wh', metavar='[0-255]', dest='webcam_hue', help='webcam hue', type=float)
group_webcam.add_argument('-ws', metavar='[0-255]', dest='webcam_saturation', help='webcam saturation', type=float)
parser.add_argument('-v', dest='verbose_debug', help='logging level DEBUG', action='store_true', default=False)
parser.add_argument('module', nargs='?', help='python module file')
args = parser.parse_args()

# Massage arguments
if str(args.input_video).lstrip('-').isdigit():
	args.input_video = int(args.input_video)


# Start logging
logging.basicConfig(
	level=(logging.DEBUG if args.verbose_debug else logging.INFO),
	format='[%(asctime)s] [%(levelname).4s] [%(filename)s:%(lineno)03d]   %(message)s',
	datefmt='%H:%M:%S'
)
logging.debug('Starting %s', os.path.splitext(__file__)[0])


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
		if modfile is not None:
			break

	dir = os.path.dirname(os.path.realpath(__file__))
	for file in os.listdir(dir):
		if file.endswith('.py') and not os.path.samefile(file, __file__):
			modfile = file
			break

# Import the Python file
if modfile is not None:
	logging.debug('Found module: %s', os.path.relpath(modfile))
	modfile = os.path.relpath(modfile)
	logging.info('Importing module: %s', modfile)
	# Add module's directory to Python's path
	moddir = os.path.dirname(os.path.abspath(modfile))
	if moddir not in sys.path:
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
	logging.error('No module to load')
	sys.exit(1)


# Main image loop
logging.debug('Opening video')
while True:
	# Open input video and set options
	cap = None
	if args.input_image is None:
		cap = cv2.VideoCapture(args.input_video)
		if cap.isOpened():
			# Get FPS from video file
			if type(args.input_video) is not int:
				args.video_fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)

			# Set video options
			if args.video_width is not None:
				cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, args.video_width)
			if args.video_height is not None:
				cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, args.video_height)
			if args.video_fps is not None:
				cap.set(cv2.cv.CV_CAP_PROP_FPS, args.video_fps)

			# Set webcam options
			if type(args.input_video) is int:
				if args.webcam_brightness is not None:
					cap.set(cv2.cv.CV_CAP_PROP_BRIGHTNESS, args.webcam_brightness/255.0)
				if args.webcam_contrast is not None:
					cap.set(cv2.cv.CV_CAP_PROP_CONTRAST, args.webcam_contrast/255.0)
				if args.webcam_exposure is not None:
					cap.set(cv2.cv.CV_CAP_PROP_EXPOSURE, args.webcam_exposure/255.0)
				if args.webcam_gain is not None:
					cap.set(cv2.cv.CV_CAP_PROP_GAIN, args.webcam_gain/255.0)
				if args.webcam_hue is not None:
					cap.set(cv2.cv.CV_CAP_PROP_HUE, args.webcam_hue/255.0)
				if args.webcam_saturation is not None:
					cap.set(cv2.cv.CV_CAP_PROP_SATURATION, args.webcam_saturation/255.0)

			logging.info('Opened video: %.fx%.f @ %.1f FPS', cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH), cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT), args.video_fps)

	# Open output video file
	out = None
	if args.output_video is not None:
		logging.debug('Opening output video: %s', args.output_video)
		fourcc = cv2.cv.CV_FOURCC(*'DIVX')
		out = cv2.VideoWriter(time.strftime(args.output_video), fourcc, args.video_fps, (int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))))

	# Set up FPS list and iterator
	times = [0] * 25
	time_idx = 0
	start = time.time()

	# Continually process frames
	while True:
		# Get a frame to process
		frame = None

		# Read input image
		if args.input_image is not None:
			if not os.path.exists(args.input_image):
				logging.error('Input image does not exist: %s', args.input_image)
				sys.exit(1)
			logging.debug('Reading image: %s', args.input_image)
			frame = sharkcv.Frame(cv2.imread(args.input_image, cv2.IMREAD_COLOR))

		# Read input video
		if cap is not None and cap.isOpened():
			ret, frame = cap.read()
			if not ret:
				if type(args.input_video) is int:
					logging.warning('Failed to read webcam frame')
				break
			frame = sharkcv.Frame(frame)

		if frame is None:
			logging.warning('Failed to get a frame')
			break


		# Execute module file
		modret = None
		try:
			modret = module(frame)
		except Exception, e:
			logging.error('Module exception: %s', str(e))
			sys.exit(1)

		# Write to output image
		if args.output_image is not None:
			logging.debug('Writing image: %s', args.output_image)
			if type(modret) is sharkcv.Frame:
				modret.writeImage(time.strftime(args.output_image))
			elif type(frame) is sharkcv.Frame and type(args.input_video) is int:
				frame.writeImage(time.strftime(args.output_image))

		# Write to output video
		if out is not None:
			# Write to output video
			if type(modret) is sharkcv.Frame:
				modret.writeVideo(out)
			elif type(frame) is sharkcv.Frame and type(args.input_video) is int:
				frame.writeVideo(out)


		# Break loop if only one frame to process
		if args.input_image is not None:
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

	# Release open output video
	if out is not None:
		out.release()

	# Release open input video
	if cap is not None:
		cap.release()

	# Break loop if using input image/video
	if args.input_image is not None or not type(args.input_video) is int:
		break

	time.sleep(0.05)
