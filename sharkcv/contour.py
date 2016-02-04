import cv2
import numpy as np

class Contour(object):
	def __init__(self, ndarray):
		self._ndarray = ndarray
		self._x = None
		self._y = None
		self._width = None
		self._height = None
		self._area = None
		self._angle = None
		self._radius = None

	def __boundingRect(self):
		self._x, self._y, self._width, self._height = cv2.boundingRect(self._ndarray)

	def __line(self):
		[vx, vy, _, _] = cv2.fitLine(self._ndarray, cv2.cv.CV_DIST_L2, 0, 0.01, 0.01)
		self._angle = np.arctan2(vy, vx)[0] * 180 / np.pi

	def __circle(self):
		(_, _), self._radius = cv2.minEnclosingCircle(self._ndarray)

	@property
	def x(self):
		if self._x is None:
			self.__boundingRect()
		return self._x

	@property
	def y(self):
		if self._y is None:
			self.__boundingRect()
		return self._y

	@property
	def width(self):
		if self._width is None:
			self.__boundingRect()
		return self._width

	@property
	def height(self):
		if self._height is None:
			self.__boundingRect()
		return self._height

	@property
	def area(self):
		if self._area is None:
			self._area = cv2.contourArea(self._ndarray)
		return self._area

	@property
	def centerX(self):
		return self.x + self.width / 2.0

	@property
	def centerY(self):
		return self.y + self.height / 2.0

	@property
	def angle(self):
		if self._angle is None:
			self.__line()
		return self._angle

	@property
	def radius(self):
		if self._radius is None:
			self.__circle()
		return self._radius