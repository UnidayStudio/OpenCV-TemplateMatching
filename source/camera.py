import cv2
import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy

from image import *

CAMERA_CALIBRATION_FRAMES = 20

class Camera():
	def __init__(self, frames, calculatedIntrinsic=None):
		self._intrinsicMat = None
		if frames != None:
			self.calibrate(frames)
		else:
			self._intrinsicMat = calculatedIntrinsic

		self.distance = None
		
	def getIntrinsicMatrix(self):
		return self._intrinsicMat
		
	def calibrate(self, frames):
		"""Fonte: https://docs.opencv.org/3.4.1/dc/dbb/tutorial_py_calibration.html"""
		
		criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

		CHESSBOARD_X = 7
		CHESSBOARD_Y = 5
		
		# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
		objp = np.zeros((CHESSBOARD_X*CHESSBOARD_Y,3), np.float32)
		objp[:,:2] = np.mgrid[0:CHESSBOARD_X,0:CHESSBOARD_Y].T.reshape(-1,2)
		
		# Arrays to store object points and image points from all the images.
		objpoints = [] # 3d point in real world space
		imgpoints = [] # 2d points in image plane.
		
		i = 0
		print("Calibration Started!")
		#while i < CAMERA_CALIBRATION_FRAMES:
		for n in range(len(frames)):
			gray = frames[n].getGrayScale()

			gray.show(2)
			
			returnValue, corners = gray.getChessBoardCorners(CHESSBOARD_X,CHESSBOARD_Y)
			#cv2.findChessboardCorners(gray, (8, 6), None)
			#print("hmm")
			if returnValue:
				print(i,"/", CAMERA_CALIBRATION_FRAMES)
				
				objpoints.append(objp)
				corners2 = cv2.cornerSubPix(gray.getSource(), corners, (11,11), (-1,-1), criteria)
				imgpoints.append(corners)

				i += 1

			if i > CAMERA_CALIBRATION_FRAMES:
				break

		print("\t...chessboard frames collected!")
		
		ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.getShape()[::-1], None, None)
		
		self._intrinsicMat = mtx
		self.distance = dist

		print("Calibration Ended!")
		print(self._intrinsicMat)
		print("dist = ", self.distance)