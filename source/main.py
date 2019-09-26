from image import *
from video import *

SOURCE_VIDEO = "project/entrada.avi"
SOURCE_MARKER = "project/alvo.jpg"
		
# (azul, verde, vermelho e ciano)		
SHAPE_COLORS = [[[255,0,0], [0,255,0],[0,0,255],[255,255,0]],
			[[255,255,0],[255,0,0], [0,255,0],[0,0,255]],
			[[0,0,255],[255,255,0],[255,0,0], [0,255,0]],
			[[0,255,0],[0,0,255],[255,255,0], [255,0,0]]]
		
def main():
	# Vídeo de entrada + lista com todos os frames (:Image())
	video = Video(SOURCE_VIDEO)
	frames = video.getFrameList()
	
	""" Aruco Markers
	* Quatro versões do aruco marker são armazenadas:
	* Uma para cada rotação possível."""
	markers = [Image(SOURCE_MARKER)]	
	for n in range(3):
		markers.append(markers[-1].getRotated90())
		
		
	for frame in frames:			
		gray = frame.getGrayScale()
		edge = gray.getEdgeImage()
		
		for contour in edge.getContours():
			for n, marker in enumerate(markers):
				warped = gray.getWarpedPerspective(contour, marker)
				
				# Se o contorno encontrado for igual ao marker, 
				# desenha o contorno com a cor certa.
				if warped == marker:
					frame.drawLines(contour, SHAPE_COLORS[n])
					break
		
		frame.show(2)

	video.release()
	cv2.destroyAllWindows()
	
# Inicialização
if __name__ == "__main__":
	main()
	





