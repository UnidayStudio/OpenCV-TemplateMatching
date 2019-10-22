from OpenGL.raw.GLUT import glutWireTeapot

import objloader
from image import *
from video import *
from camera import *

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

SOURCE_VIDEO = "entrada.avi"
SOURCE_MARKER = "alvo.jpg"

CALCULATE_INTRINSIC_MATRIX = True

# (azul, verde, vermelho e ciano)   	
SHAPE_COLORS = [[[255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 0]],
				[[255, 255, 0], [255, 0, 0], [0, 255, 0], [0, 0, 255]],
				[[0, 0, 255], [255, 255, 0], [255, 0, 0], [0, 255, 0]],
				[[0, 255, 0], [0, 0, 255], [255, 255, 0], [255, 0, 0]]]

verticies = (
	(1, -1, -1),
	(1, 1, -1),
	(-1, 1, -1),
	(-1, -1, -1),
	(1, -1, 1),
	(1, 1, 1),
	(-1, -1, 1),
	(-1, 1, 1)
)

uvs = (
	(0, 0),
	(1, 0),
	(1, 1),
	(0, 1),
)

surfaces = (
	(0, 1, 2, 3),
	(3, 2, 7, 6),
	(6, 7, 5, 4),
	(4, 5, 1, 0),
	(1, 5, 7, 2),
	(4, 0, 3, 6)
)


def drawObject():
	glBegin(GL_QUADS)
	glColor3fv([1, 0, 0])
	for surface in surfaces:
		x = 0
		for vertex in surface:
			glTexCoord2fv(uvs[x])
			x += 1
			v = verticies[vertex]
			# glVertex3fv()
			scale = 1
			glVertex3f(v[0] * scale, v[1] * scale, v[2] * scale)
	glEnd()


def drawPlane(height, width):
	glBegin(GL_QUADS)
	glColor3fv([1, 1, 1])
	for n in range(4):
		glTexCoord2fv(uvs[n])
		glVertex2fv(uvs[n])
	glEnd()
	"""glPushMatrix()
	glBegin(GL_QUADS)
	glTexCoord2i(0, 0); glVertex2i(0, 0)
	glTexCoord2i(1, 0); glVertex2i(width, 0)
	glTexCoord2i(1, 1); glVertex2i(width, height)
	glTexCoord2i(0, 1); glVertex2i(0, height)
	glEnd()
	glPopMatrix()"""




def main():
	# Vídeo de entrada + lista com todos os frames (:Image())
	video = Video(SOURCE_VIDEO)
	frames = video.getFrameList()

	""" Aruco Markers
	* Quatro versões do aruco marker são armazenadas:
	* Uma para cada rotação possível."""
	global markers
	markers = [Image(SOURCE_MARKER)]
	for n in range(3):
		markers.append(markers[-1].getRotated90())

	#global camera
	camera = None
	if CALCULATE_INTRINSIC_MATRIX:
		camera = Camera(frames)
	else:
		camera = Camera(None, np.mat("306.15951514 0.0 306.99696673; 0.0 255.6431554 250.73583755; 0.0 0.0 1.0"))


	pygame.init()
	display = (640, 480)
	screen = pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
	pygame.display.set_caption("ICV")

	fx = camera.getIntrinsicMatrix()[0][0]
	fy = camera.getIntrinsicMatrix()[1][1]
	fovy = 2*np.arctan(0.5*display[1]/fy)*180/np.pi
	aspect = (display[0]*fx)/(display[1]*fy)

	gluPerspective(fovy, aspect, 0.1, 150.0)

	glMatrixMode(GL_MODELVIEW)

	glEnable(GL_TEXTURE_2D)

	pikachu = objloader.OBJ('Pikachu.obj', swapyz=True)

	bg_id = glGenTextures(1)

	glEnable(GL_TEXTURE_2D)
	glBindTexture(GL_TEXTURE_2D, bg_id)

	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

	for frame in frames:
		glClearColor(0.0, 0.0, 0.0, 0.0)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

		"""if not videoStore.isOpened():
			videoStore.release()
			return"""

		videoStore = video.getSource()

		#ok, frame = videoStore.read()
		gray = frame.getGrayScale()
		edge = gray.getEdgeImage()

		# /* load_background

		"""bg_img = cv2.cvtColor(frame.getSource(), cv2.COLOR_BGR2RGB)
		bg_img = cv2.flip(bg_img, 0)
		height, width, channels = bg_img.shape
		bg_img = np.frombuffer(bg_img.tostring(), dtype=bg_img.dtype)
		bg_img.shape = (height, width, channels)"""

		bg_img = frame.getSource().tobytes();

		#height, width, channels = frame.getShape()
		width, height = 640, 480

		#bg_id = glGenTextures(1)

		glEnable(GL_TEXTURE_2D)
		glActiveTexture(GL_TEXTURE0)
		glBindTexture(GL_TEXTURE_2D, bg_id)

		#glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		#glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, bg_img)

		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(0, width, 0, height)

		#glBindTexture(GL_TEXTURE_2D, bg_id)
		#glTexImage2D(GL_TEXTURE_2D, 0, 3, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, bg_img)

		drawPlane(height, width)
		"""glPushMatrix()
		glBegin(GL_QUADS)
		glTexCoord2i(0, 0); glVertex2i(0, 0)
		glTexCoord2i(1, 0); glVertex2i(width, 0)
		glTexCoord2i(1, 1); glVertex2i(width, height)
		glTexCoord2i(0, 1); glVertex2i(0, height)
		glEnd()
		glPopMatrix()"""
		glBindTexture(GL_TEXTURE_2D, 0)

		# load_background *\

		glMatrixMode(GL_PROJECTION)
		gluPerspective(fovy, aspect, 0.1, 150.0)

		objp = np.zeros((6 * 7, 3), np.float32)
		objp[:, :2] = np.mgrid[0:7, 0:6].T.reshape(-1, 2)

		for contour in edge.getContours():
			for n, marker in enumerate(markers):
				warped = gray.getWarpedPerspective(contour, marker)

				# Se o contorno encontrado for igual ao marker,
				# desenha o contorno com a cor certa.
				if warped == marker:
					imagePoints = np.array(contour, dtype="float32")
					objectPoints = np.array([[-1, -1, 1], [1, -1, 1],
											 [1, 1, 1], [-1, 1, 1]], dtype="float32")
					flag, rvecs, tvecs = cv2.solvePnP(objectPoints, imagePoints, camera.getIntrinsicMatrix(),
													  camera.distance)  # , flags=cv2.SOLVEPNP_ITERATIVE)
					# print(flag, rvecs, tvecs)

					rotm = cv2.Rodrigues(rvecs)[0]

					m = np.array([[rotm[0][0], rotm[0][1], rotm[0][2], tvecs[0]],
								  [rotm[1][0], rotm[1][1], rotm[1][2], tvecs[1]],
								  [rotm[2][0], rotm[2][1], rotm[2][2], tvecs[2]],
								  [0.0, 0.0, 0.0, 1.0]])

					m = m * np.array([[1.0, 1.0, 1.0, 1.0],
									  [-1.0, -1.0, -1.0, -1.0],
									  [-1.0, -1.0, -1.0, -1.0],
									  [1.0, 1.0, 1.0, 1.0]])
					m = np.transpose(m)

					# the Object
					# glEnable(GL_DEPTH_TEST)

					glMatrixMode(GL_MODELVIEW)
					glLoadIdentity()
					glPushMatrix()
					glLoadMatrixd(m)

					# drawObject()
					# glutWireTeapot(0.5)
					glCallList(pikachu.gl_list)
					glPopMatrix()

		#glutSwapBuffers()

		quit = False
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quit = True
				break
		if quit:
			break
		pygame.display.flip()

	pygame.quit()

	"""fx = camera.getIntrinsicMatrix()[0][0]
	fy = camera.getIntrinsicMatrix()[1][1]
	global fovy
	fovy = 2 * np.arctan(0.5 * 480 / fy) * 180 / np.pi
	global aspect
	aspect = (200 * fx / 480 * fy)

	global videoStore


   videoStore = cv2.VideoCapture(SOURCE_VIDEO)
	glutInit()
	glutInitDisplayMode(GLUT_RGB | GLUT_DEPTH | GLUT_DOUBLE)
	glutInitWindowSize(640, 480)  # SET WINDOW SIZE
	glutInitWindowPosition(200, 200)  # SET WINDOW POSITION
	window = glutCreateWindow("OpenGL")  # CREATE WINDOW
	global pikachu
	pikachu = objloader.OBJ('Pikachu.obj', swapyz=True)
	glutDisplayFunc(draw)  # DISPLAY CALLBACK
	glutIdleFunc(glutPostRedisplay())  # IDLE CALLBACK
	glutMainLoop()  # INIT LOOP"""


# Inicialização
if __name__ == "__main__":
	main()
