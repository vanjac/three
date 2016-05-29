__author__ = "vantjac"

import threelib.edit.editor

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import pyautogui

# based on PyOpenGl NeHe tutorial

# the editor
editor = None

# Number of the glut window - will be set when the window is created
window = 0

# Global projection settings
# Call resetProjection() if any of these are changed
aspect = 1 # aspect ratio of the window (width / height)
windowWidth = 1
windowHeight = 1
fov = 60 # field of view
nearClip = 0.1
farClip = 100.0

# Mouse info
mouseButtonPressed = [ False for i in range(0, 7) ]
pmouseX = 0
pmouseY = 0
mouseLocked = False

mouseLockMargin = 64
framesSinceMouseLockMove = 0

class EditorMain:
    # General OpenGL initialization function.
    def initGL(width, height):
        global windowWidth, windowHeight
    
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0) # enables clearing of depth buffer
        glDepthFunc(GL_LESS) # type of depth test to use
        glEnable(GL_DEPTH_TEST) # enable depth testing
        glShadeModel(GL_SMOOTH) # enable smooth color shading

        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
    
        windowWidth = width
        windowHeight = height
        EditorMain.resetProjection()

        editor.init()
    
    # Called when window is resized
    def resizeGL(width, height):
        global aspect, windowWidth, windowHeight
        if height == 0: # prevent divide by zero error 
            height = 1
    
        windowWidth = width
        windowHeight = height
        # reset the current viewport and perspective transformation
        glViewport(0, 0, width, height)
        EditorMain.resetProjection()

    # should be called if any settings like aspect
    # ratio, fov, near/far clip planes, have changed.
    def resetProjection():
        global aspect, fov, nearClip, farClip, windowWidth, windowHeight
        aspect = float(windowWidth) / float(windowHeight)
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

    def lockMouse():
        global mouseLocked
        mouseLocked = True
        glutSetCursor(GLUT_CURSOR_NONE)

    def unlockMouse():
        global mouseLocked
        mouseLocked = False
        glutSetCursor(GLUT_CURSOR_INHERIT)

    def mouseMovement(mouseX, mouseY):
        global editor, pmouseX, pmouseY, mouseLocked, mouseLockMargin
        global windowWidth, windowHeight, framesSinceMouseLockMove

        # ignore mouse movements created by locking
        if (abs(mouseX - pmouseX) > windowWidth / 2 
            or abs(mouseY - pmouseY) > windowHeight / 2):
            pmouseX = mouseX
            pmouseY = mouseY
            return

        editor.mouseMoved(mouseX, mouseY, pmouseX, pmouseY)
        framesSinceMouseLockMove += 1
        if mouseLocked and framesSinceMouseLockMove > 4:
            if mouseX > windowWidth - mouseLockMargin:
                pyautogui.moveRel(-windowWidth + 3*mouseLockMargin, 0)
                framesSinceMouseLockMove = 0
            if mouseX < mouseLockMargin:
                pyautogui.moveRel(windowWidth - 3*mouseLockMargin, 0)
                framesSinceMouseLockMove = 0
            if mouseY > windowHeight - mouseLockMargin:
                pyautogui.moveRel(0, -windowHeight + 3*mouseLockMargin)
                framesSinceMouseLockMove = 0
            if mouseY < mouseLockMargin:
                pyautogui.moveRel(0, windowHeight - 3*mouseLockMargin)
                framesSinceMouseLockMove = 0
        pmouseX = mouseX
        pmouseY = mouseY

    # pass in an EditorState to initialize the Editor with that state
    def main(state=None):
        global window, editor

        width = 1024
        height = 736
        
        editor = threelib.edit.editor.Editor(EditorMain, state)
        
        # pass arguments to init
        glutInit(sys.argv)
        
        # Select type of display mode:   
        #  Double buffer 
        #  RGBA color
        #  Alpha components supported 
        #  Depth buffer
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)

        glutInitWindowSize(width, height)
        glutInitWindowPosition(0, 0)
        
        # Retain window id to use when closing
        # global variable
        window = glutCreateWindow("three editor")
        
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
        EditorMain.initGL(width, height)
        
        # Start Event Processing Engine	
        glutMainLoop()
        
if __name__=="__main__":
    EditorMain.main()

