import cv2
import numpy as np

import sharkcv


class Frame(object):
	def __init__(self, ndarray, **kwargs):
		self._ndarray = ndarray
		self._color = 'BGR'
		if 'color' in kwargs:
			self._color = kwargs['color']
		self._contours = None

	@property
	def width(self):
		return self._ndarray.shape[1]
	@property
	def height(self):
		return self._ndarray.shape[0]

	# Change the colorspace of this frame
	# http://docs.opencv.org/java/2.4.7/org/opencv/imgproc/Imgproc.html
	def __color(self, name):
		# Change colorspace only if different
		if name != self._color:
			try:
				imgproc = getattr(cv2, 'COLOR_' + self._color + '2' + name)
				self._ndarray = cv2.cvtColor(self._ndarray, imgproc)
				self._color = name
			except:
				return False
		return True
	def colorBGR(self):
		return self.__color('BGR')
	def colorBGRA(self):
		return self.__color('BGRA')
	def colorGRAY(self):
		return self.__color('GRAY')
	def colorHLS(self):
		return self.__color('HLS')
	def colorHSV(self):
		return self.__color('HSV')
	def colorRGB(self):
		return self.__color('RGB')
	def colorRGBA(self):
		return self.__color('RGBA')

	# Return a mask frame of threshold-ed pixels
	def threshold(self, lower, upper):
		return sharkcv.Frame(cv2.inRange(self._ndarray, np.array(lower), np.array(upper)))

	# Resize this frame
	def resize(self, width, height):
		# Assume width/height in [0,1] is a percent
		if width < 1 and height < 1:
			width = self.width * width
			height = self.height * height
		# Resize only if different
		if width != self.width or height != self.height:
			self._ndarray = cv2.resize(self._ndarray, (width,height), interpolation=cv2.INTER_LINEAR)
			self._contours = None

	# Move the frame while keeping same width/height
	def translate(self, x, y):
		matrix = np.float32([[1,0,x],[0,1,y]])
		self._ndarray = cv2.warpAffine(self._ndarray, matrix, (self.width,self.height))
		self._contours = None

	# Rotate the frame while keeping same width/height
	def rotate(self, deg):
		matrix = cv2.getRotationMatrix2D((self.width/2,self.height/2), deg, 1)
		self._ndarray = cv2.warpAffine(self._ndarray, matrix, (self.width,self.height))
		self._contours = None

	# Blur this frame with a box filter
	def blur(self, size):
		self._ndarray = cv2.blur(self._ndarray, (size,size))
		self._contours = None

	# Blur this frame with a Gaussian kernel
	def blurGaussian(self, size):
		self._ndarray = cv2.GaussianBlur(self._ndarray, (size,size), 0)
		self._contours = None

	# Blur this frame with a median filter
	def blurMedian(self, size):
		self._ndarray = cv2.medianBlur(self._ndarray, size)
		self._contours = None

	# Write this frame to an image
	def writeImage(self, filename):
		cv2.imwrite(filename, self._ndarray)

	# Write this frame to a video (VideoWriter)
	def writeVideo(self, video_writer):
		video_writer.write(self._ndarray)

	# Build an array of contours
	@property
	def contours(self):
		if self._contours is None:
			self._contours = []
			try:
				contours, hierarchy = cv2.findContours(self._ndarray, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)
				for contour in contours:
					self._contours.append(sharkcv.Contour(contour))
			except:
				pass
		return self._contours

	# Filter contours by any sharkcv.Contour property
	def contoursFilter(self, **kwargs):
		for prop in kwargs.keys():
			range = kwargs[prop]
			i = 0
			while i < len(self.contours):
				value = getattr(self.contours[i], prop)
				if range[0] is not None and range[0] >= 0:
					if value < range[0]:
						del self.contours[i]
						continue
				if range[1] is not None and range[1] >= 0:
					if value > range[1]:
						del self.contours[i]
						continue
				i += 1

	# Sort contours by any sharkcv.Contour property
	def contoursSort(self, prop, descending=True):
		self._contours = sorted(self.contours, key=lambda c: getattr(c,prop), reverse=descending)

	# Draw this frame's contours onto another frame
	def contoursDraw(self, frame, **kwargs):
		if 'color' not in kwargs:
			kwargs['color'] = (0,255,0)
		if 'width' not in kwargs:
			kwargs['width'] = 2
		contours = [cnt._ndarray for cnt in self.contours]
		if len(contours) > 0:
			cv2.drawContours(frame._ndarray, contours, -1, kwargs['color'], kwargs['width'])
			return True
		return False

	# Dilate this mask's white region
	def dilate(self, **kwargs):
		if 'shape' not in kwargs:
			kwargs['shape'] = cv2.MORPH_ELLIPSE
		if 'size' not in kwargs:
			kwargs['size'] = 3
		if 'iterations' not in kwargs:
			kwargs['iterations'] = 1
		kernel = cv2.getStructuringElement(kwargs['shape'], (kwargs['size'],kwargs['size']))
		self._ndarray = cv2.dilate(self._ndarray, kernel, kwargs['iterations'], borderType=cv2.BORDER_CONSTANT)
		self._contours = None

	# Erode this mask's white region
	def erode(self, **kwargs):
		if 'shape' not in kwargs:
			kwargs['shape'] = cv2.MORPH_ELLIPSE
		if 'size' not in kwargs:
			kwargs['size'] = 3
		if 'iterations' not in kwargs:
			kwargs['iterations'] = 1
		kernel = cv2.getStructuringElement(kwargs['shape'], (kwargs['size'],kwargs['size']))
		self._ndarray = cv2.erode(self._ndarray, kernel, kwargs['iterations'], borderType=cv2.BORDER_CONSTANT)
		self._contours = None

	# Erode/dilate this mask's white area
	def open(self, **kwargs):
		if 'shape' not in kwargs:
			kwargs['shape'] = cv2.MORPH_ELLIPSE
		if 'size' not in kwargs:
			kwargs['size'] = 3
		kernel = cv2.getStructuringElement(kwargs['shape'], (kwargs['size'],kwargs['size']))
		self._ndarray = cv2.morphologyEx(self._ndarray, cv2.MORPH_OPEN, kernel)
		self._contours = None

	# Dilate/erode this mask's white area
	def close(self, **kwargs):
		if 'shape' not in kwargs:
			kwargs['shape'] = cv2.MORPH_ELLIPSE
		if 'size' not in kwargs:
			kwargs['size'] = 3
		kernel = cv2.getStructuringElement(kwargs['shape'], (kwargs['size'],kwargs['size']))
		self._ndarray = cv2.morphologyEx(self._ndarray, cv2.MORPH_CLOSE, kernel)
		self._contours = None

	# AND this frame with another frame
	def bit_and(self, frame):
		self._ndarray = cv2.bitwise_and(self._ndarray, frame._ndarray)
		self._contours = None

	# OR this frame with another frame
	def bit_or(self, frame):
		self._ndarray = cv2.bitwise_or(self._ndarray, frame._ndarray)
		self._contours = None

	# NOT this frame with another frame
	def bit_not(self, frame):
		self._ndarray = cv2.bitwise_not(self._ndarray, frame._ndarray)
		self._contours = None

	# XOR this frame with another frame
	def bit_xor(self, frame):
		self._ndarray = cv2.bitwise_xor(self._ndarray, frame._ndarray)
		self._contours = None