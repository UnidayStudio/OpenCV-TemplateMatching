import cv2
import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy

from image import *

		
class Video():
	def __init__(self, source):
		self._source = cv2.VideoCapture(source)

	def getSource(self):
		return self._source
	
	def getFrameList(self, showImages=False):
		"""Retorna uma lista com todos os frames do vídeo."""
		out = []
		x = 0
		while True:
			frame = self.getFrame(showImages)
			if not frame[0]:
				break
				
			out.append(frame[1])
			#print("frame... ", x)
			x+=1
		
		if showImages:
			cv2.destroyAllWindows()
		return out
	
	def getFrame(self, showImage=False):
		"""Retorna uma tupla contendo True ou False se há framesrestantes e 
		o próximo frame disponível do vídeo (se houver)."""
		returnValue, source = self._source.read()
		
		if not returnValue:
			return False, None
					
		image = Image(source) 
		
		if showImage:
			image.show(2)
			
		return True, image
		
	def release(self):
		"""Libera o vídeo carregado pelo openCV."""
		self._source.release()
	
