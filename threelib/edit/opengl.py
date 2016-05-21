__author__ = "vantjac"

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# based on PyOpenGl NeHe tutorial

# Number of the glut window.
# Will be set when the window is created
window = 0

# General OpenGL initialization function.
def initGL(width, height):
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0) # enables clearing of depth buffer
    glDepthFunc(GL_LESS) # type of depth test to use
    glEnable(GL_DEPTH_TEST) # enable depth testing
    glShadeModel(GL_SMOOTH) # enable smooth color shading
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity() # reset projection matrix
    # calculate aspect ratio of window
    gluPerspective(45.0, float(width)/float(height), 0.1, 100.0)
    
    glMatrixMode(GL_MODELVIEW)
    
# Called when window is resized
def resizeGL(Width, Height):
    if Height == 0: # prevent divide by zero error 
        Height = 1
        
    # reset the current viewport and perspective transformation
    glViewport(0, 0, Width, Height) 
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    
# The main drawing function. 
def drawGL():
    # clear screen and depth buffer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity() # reset the view 
    
    glTranslate(0, 0, -5)
    glRotate(30, 0, 1, 0)
    
    
    glBegin(GL_TRIANGLES)
    glColor(1.0, 0.0, 0.0)
    glVertex(0.0, 1.0, 0.0)
    glColor(0.0, 1.0, 0.0)
    glVertex(1.0, -1.0, 0.0)
    glColor(0.0, 0.0, 1.0)
    glVertex(-1.0, -1.0, 0.0)
    glEnd()
    
    #  double buffered - swap the buffers to display what just got drawn. 
    glutSwapBuffers()


# info passed as tuple: (key, mouseX, mouseY)  
def keyPressed(*args):
    print(args)
    if args[0] == b'q':
        sys.exit()

# info passed as tuple: (button, eventType, mouseX, mouseY)
# button: left=0, middle=1, right=2, 
#   scroll-up=3, scroll-down=4, scroll-left=5, scroll-right=6
# eventType: mousePressed=0, mouseReleased=1
def mouseEvent(*args):
    print(args)

# info passed as tuple: (mouseX, mouseY)
def mouseMoved(*args):
    print(args)

def main():
    global window
    # pass arguments to init
    glutInit(sys.argv)

    # Select type of display mode:   
    #  Double buffer 
    #  RGBA color
    #  Alpha components supported 
    #  Depth buffer
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    
    # get a 640 x 480 window 
    glutInitWindowSize(640, 480)
    
    # the window starts at the upper left corner of the screen 
    glutInitWindowPosition(0, 0)
    
    # Retain window id to use when closing
    # global variable
    window = glutCreateWindow("Test Window")
    
    # Uncomment this line to get full screen.
    #glutFullScreen()

    # Register important functions
    glutDisplayFunc(drawGL)
    glutIdleFunc(drawGL)
    glutReshapeFunc(resizeGL)
    glutKeyboardFunc(keyPressed)
    glutMouseFunc(mouseEvent)
    glutPassiveMotionFunc(mouseMoved)
    
    # Initialize our window. 
    initGL(640, 480)
    
    # Start Event Processing Engine	
    glutMainLoop()
    
main()
		
