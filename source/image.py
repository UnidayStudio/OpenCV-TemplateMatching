import cv2
import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy

IMAGE_COMPARE_THRESHOLD = 0.78
WINDOW_TITLE = "Frame"

class Image():
	RAW_IMAGE = 0
	GRAY_IMAGE = 1
	EDGE_IMAGE = 2 # Canny

	def __init__(self, source, imageType=RAW_IMAGE):
		"""Carrega e armazena uma imagem do OpenCV através de um 
		arquivo fonte ou de uma imagem já carregada."""
		self._source = None
		self._type = imageType
		
		if isinstance(source, str):
			self._source = cv2.imread(source, 0)
		else:
			self._source = source
			
		self.points = None
		self.update()
			
	def update(self):
		"""Obtém os pontos do shape da imagem."""
		shape = self._source.shape
		self.points = np.array([[0,0], [0,shape[1]], 
			[shape[0], shape[1]], [shape[0], 0]])
		
	def __eq__(self, other):
		"""Usa o algoritmo de <Normalized cross correlation (NCC)> para obter
		um score de similaridade entre as duas imagens e, baseado em um limiar
		(macro IMAGE_COMPARE_THRESHOLD), retorna True ou False para definir se
		as duas imagens são iguais."""		
		source1 = self._source.astype(float)
		source2 = other._source.astype(float)
		
		numerator = np.sum(np.multiply(source1, source2))
		denominator = np.sum(np.multiply(source1, source1))
		denominator *= np.sum(np.multiply(source2, source2))
		denominator = np.sqrt(denominator)
		
		res = (numerator/denominator)
		
		return res > IMAGE_COMPARE_THRESHOLD
	
	def _cv2Rotate90(self):
		"""Método protegido que rotaciona a imagem em 90 graus.
		É necessário para fazer o template matching."""
		center = (self._source.shape[0]/2, self._source.shape[1]/2)
		rotationMatrix = cv2.getRotationMatrix2D(center, 90, 1.0)
		
		size = (self._source.shape[1], self._source.shape[0])
		return cv2.warpAffine(self._source, rotationMatrix, size)
		
	def getCopy(self):
		"""Retorna uma cópia da classe."""
		return Image(self._source.copy(), self._type)
	
	def getRotated90(self):
		"""Retorna uma nova instância da classe mas com a imagem
		rotacionada em 90 graus."""
		return Image(self._cv2Rotate90(), self._type)
		
	def rotate90(self):
		"""Rotaciona a imagem da instância da classe em 90 graus."""
		self._source = self._cv2Rotate90()
		self.update()
		
	def getGrayScale(self):
		"""Retorna uma nova instância da classe com a imagem atual em
		escala de cinza. Necessário para aplicar o algoritmo de detecção
		de arestas (Canny)."""
		return Image(cv2.cvtColor(self._source, cv2.COLOR_BGR2GRAY), self.GRAY_IMAGE)
			
	def getEdgeImage(self):
		"""Retorna uma nova instância da classe com a imagem atual após
		a detecção de arestas através do algoritmo de Canny."""
		out = cv2.Canny(self._source, 100, 200)
		return Image(out, self.EDGE_IMAGE)
		
	def getContours(self):
		"""Retorna uma lista com todos os vértices de todos os contornos encontrados."""
		assert(self._type == self.EDGE_IMAGE),("Error: Only edge images can be used to find contours!")
		
		contours, hierarchy = cv2.findContours(self._source, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
		
		out = []
		for i in range(len(contours)):
			if hierarchy[0][i][3] == -1:
				#Poda: contornos quadrados são sempre convexos e com 4 arestas.
				epsilon = 0.1*cv2.arcLength(contours[i], True)
				approx = cv2.approxPolyDP(contours[i], epsilon, True)
				
				if len(approx) == 4 and cv2.isContourConvex(approx):
					out.append(approx)
		
		return out
				
	def getWarpedPerspective(self, inputContour, imageMarker):
		"""Calcula a homografia e projeta a área de entrada (inputContour)
		em uma nova imagem."""
		H, mask = cv2.findHomography(inputContour, imageMarker.points)
		source = cv2.warpPerspective(self._source, H, imageMarker._source.shape)
		return Image(source, self._type)
		
	def getChessBoardCorners(self, x, y):
		"""Obtém a localização do padrão do quadro de xadrez, nenessário para 
		a calibração da câmera."""
		returnValue, corners = cv2.findChessboardCorners(self._source, (x, y), None)
		
		if returnValue == True:
			return corners
		return None
		
	def show(self, waitTime=0):
		"""Exibe a imagem em uma janela do sistema."""
		source = self._source
		cv2.imshow(WINDOW_TITLE, source)
		cv2.waitKey(waitTime)
		
	def drawContour(self, contour, color):
		"""Desenha as arestas de um contorno na imagem com uma cor única."""
		cv2.drawContours(self._source, [contour], -1, color, 2)
		
		
	def drawLines(self, contour, colors):
		"""Desenha as arestas de um contorno na imagem com quatro cores
		diferentes."""
	
		for n in range(4):
			p1 = contour[n%4][0]
			p1 = (p1[0], p1[1])
			p2 = contour[(n+1)%4][0]
			p2 = (p2[0], p2[1])
			
			cv2.line(self._source, p1, p2, colors[n], 5)
		
		