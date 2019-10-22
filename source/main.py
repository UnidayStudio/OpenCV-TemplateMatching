from image import *
from video import *
from camera import *

import objloader

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

SOURCE_VIDEO = "entrada.avi"
SOURCE_MARKER = "alvo.jpg"


def drawPlane(height, width):
	glPushMatrix()
	glBegin(GL_QUADS)
	glTexCoord2i(0, 1); glVertex2i(0, 0)
	glTexCoord2i(1, 1); glVertex2i(width, 0)
	glTexCoord2i(1, 0); glVertex2i(width, height)
	glTexCoord2i(0, 0); glVertex2i(0, height)
	glEnd()
	glPopMatrix()

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

	camera = Camera(frames)

	pygame.init()
	width = 480
	height = 640
	display = (height, width)
	screen = pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
	pygame.display.set_caption("ICV")

	fx = camera.getIntrinsicMatrix()[0][0]
	fy = camera.getIntrinsicMatrix()[1][1]
	fovy = 2*np.arctan(0.5*display[1]/fy)*180/np.pi
	#fovy *= 1.1

	aspect = (display[0]*fx)/(display[1]*fy)

	clipStart = 0.1
	clipEnd = 150.0

	glMatrixMode(GL_PROJECTION)
	gluPerspective(fovy, aspect, clipStart, clipEnd)

	#glMatrixMode(GL_MODELVIEW)

	glEnable(GL_TEXTURE_2D)

	textureID = glGenTextures(1)

	pikachu = objloader.OBJ('Pikachu.obj', swapyz=True)	
		
	for frame in frames:			
		gray = frame.getGrayScale()
		edge = gray.getEdgeImage()

		# OpenGL Texture stuff...
		glEnable(GL_TEXTURE_2D)
		glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
		glActiveTexture(GL_TEXTURE0)
		glBindTexture(GL_TEXTURE_2D, textureID)
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 640, 480, 0,GL_RGB, GL_UNSIGNED_BYTE, frame.getSource().tobytes())
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

		# Texture background...
		glDisable(GL_DEPTH_TEST)

		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(0, width, 0, height)
		drawPlane(height, width)

		glBindTexture(GL_TEXTURE_2D, 0)

		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(fovy, aspect, clipStart, clipEnd)

		glEnable(GL_DEPTH_TEST)

		for contour in edge.getContours():
			for n, marker in enumerate(markers):
				warped = gray.getWarpedPerspective(contour, marker)
				
				# Se o contorno encontrado for igual ao marker, 
				# desenha o contorno com a cor certa.
				if warped == marker:
					imagePoints = np.array(contour, dtype="float32")
					objectPoints = np.array([[-1,-1, 1],[ 1,-1, 1],
											 [ 1, 1, 1],[-1, 1, 1]], dtype="float32")
					flag, rvecs, tvecs = cv2.solvePnP(objectPoints, imagePoints, camera.getIntrinsicMatrix(), 
						camera.distance)#, flags=cv2.SOLVEPNP_ITERATIVE)
					#print(flag, rvecs, tvecs)

					rotm = cv2.Rodrigues(rvecs)[0]

					m = np.array([[rotm[0][0], rotm[0][1], rotm[0][2], tvecs[0]],
								  [rotm[1][0], rotm[1][1], rotm[1][2], tvecs[1]],
								  [rotm[2][0], rotm[2][1], rotm[2][2], tvecs[2]],
								  [       0.0,        0.0,        0.0,      1.0]])

					m = m * np.array([[ 1.0, 1.0, 1.0, 1.0],
									  [-1.0,-1.0,-1.0,-1.0],
									  [-1.0,-1.0,-1.0,-1.0],
									  [ 1.0, 1.0, 1.0, 1.0]])
					m = np.transpose(m)

					#print(m)

					# the Object
					glMatrixMode(GL_MODELVIEW)
					glLoadIdentity()
					glPushMatrix()
					glLoadMatrixd(m)
					glCallList(pikachu.gl_list)
					glPopMatrix()
					break
		
		#frame.show(2)

		quit = False
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quit = True
				break
		if quit:
			break
		pygame.display.flip()

	video.release()
	cv2.destroyAllWindows()

	pygame.quit()
	
# Inicialização
if __name__ == "__main__":
	main()
	





