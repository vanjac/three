__author__ = "vantjac"

import threelib.edit.editor

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# based on PyOpenGl NeHe tutorial

# the editor
editor = None

# Number of the glut window - will be set when the window is created
window = 0

# Global projection settings
# Call resetProjection() if any of these are changed
aspect = 1 # aspect ratio of the window (width / height)
fov = 60 # field of view
nearClip = 0.1
farClip = 100.0

# Mouse info
mouseButtonPressed = [ False for i in range(0, 7) ]
pmouseX = 0
pmouseY = 0

class EditorMain:
    # General OpenGL initialization function.
    def initGL(width, height):
        global aspect
    
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0) # enables clearing of depth buffer
        glDepthFunc(GL_LESS) # type of depth test to use
        glEnable(GL_DEPTH_TEST) # enable depth testing
        glShadeModel(GL_SMOOTH) # enable smooth color shading
    
        aspect = float(width) / float(height)
        EditorMain.resetProjection()
    
    # Called when window is resized
    def resizeGL(width, height):
        global aspect
        if height == 0: # prevent divide by zero error 
            height = 1
    
        # reset the current viewport and perspective transformation
        glViewport(0, 0, width, height) 
        aspect = float(width) / float(height)
        EditorMain.resetProjection()

    # should be called if any settings like aspect
    # ratio, fov, near/far clip planes, have changed.
    def resetProjection():
        global aspect, fov, nearClip, farClip
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(fov, aspect, nearClip, farClip)
        glMatrixMode(GL_MODELVIEW)
        
    # The main drawing function. 
    def drawGL():
        # clear screen and depth buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity() # reset the view 
        editor.draw()
        #  double buffered - swap the buffers to display what just got drawn. 
        glutSwapBuffers()

    # info passed as tuple: (button, eventType, mouseX, mouseY)
    # button: left=0, middle=1, right=2, 
    #   scroll-up=3, scroll-down=4, scroll-left=5, scroll-right=6
    # eventType: mousePressed=0, mouseReleased=1
    def mouseEvent(*args):
        global mouseButtonPressed, editor
        button = args[0]
        pressed = args[1] == 0
        mouseButtonPressed[button] = pressed
        if pressed:
            editor.mousePressed(button, args[2], args[3])
        else:
            editor.mouseReleased(button, args[2], args[3])

    def buttonPressed(button=0):
        return mouseButtonPressed[button]

    def mouseMovement(mouseX, mouseY):
        global editor, pmouseX, pmouseY
        editor.mouseMoved(mouseX, mouseY, pmouseX, pmouseY)
        pmouseX = mouseX
        pmouseY = mouseY

    def main():
        global window, editor
        editor = threelib.edit.editor.Editor(EditorMain)
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
        glutDisplayFunc(EditorMain.drawGL)
        glutIdleFunc(EditorMain.drawGL)
        glutReshapeFunc(EditorMain.resizeGL)
        glutKeyboardFunc(editor.keyPressed)
        glutKeyboardUpFunc(editor.keyReleased)
        glutMouseFunc(EditorMain.mouseEvent)
        glutPassiveMotionFunc(EditorMain.mouseMovement)
        
        # Initialize our window. 
        EditorMain.initGL(640, 480)
        
        # Start Event Processing Engine	
        glutMainLoop()
        
if __name__=="__main__":
    EditorMain.main()

