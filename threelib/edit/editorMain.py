__author__ = "vantjac"

import threelib.edit.editor
import time # for fps

import pyautogui

import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

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
nearClip = 4
farClip = 2048.0

# Mouse info
mouseButtonPressed = [ False for i in range(0, 7) ]
pmouseX = 0
pmouseY = 0
mouseLocked = False
# position mouse was locked at
mouseLockX = 0
mouseLockY = 0

mouseLockMargin = 64
framesSinceMouseLockMove = 0

lastFpsTime = time.time()
fpsCount = 0
fps = 0

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
        global lastFpsTime, fpsCount, fps

        fpsCount += 1
        
        seconds = time.time()
        if seconds - lastFpsTime > 1:
            lastFpsTime = seconds
            fps = fpsCount
            fpsCount = 0

        # clear screen and depth buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity() # reset the view
        
        editor.draw()
        
        if glGetError() != GL_NO_ERROR:
            print("GL Error!")
        
        #  double buffered - swap the buffers to display what just got drawn. 
        glutSwapBuffers()

    def getFps():
        global fps
        return fps

    def getAspect():
        global aspect
        return aspect

    def getFOV():
        global fov
        return fov

    def drawText(text, font, x, y):
        global windowWidth, windowHeight
        depthEnabled = glIsEnabled(GL_DEPTH_TEST)
        glDisable(GL_DEPTH_TEST)
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0.0, windowWidth, 0.0, windowHeight)

        glRasterPos(x,y)
        for c in text :
            glutBitmapCharacter(font, ctypes.c_int(ord(c)))
        
        if depthEnabled:
            glEnable(GL_DEPTH_TEST)

        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

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

    def shiftPressed():
        return glutGetModifiers(GLUT_ACTIVE_SHIFT) != 0

    def ctrlPressed():
        return glutGetModifiers(GLUT_ACTIVE_CTRL) != 0

    def altPressed():
        return glutGetModifiers(GLUT_ACTIVE_ALT) != 0

    def mouseX():
        global pmouseX
        return pmouseX

    def mouseY():
        global pmouseY
        return pmouseY

    def lockMouse():
        global mouseLocked, pmouseX, pmouseY, mouseLockX, mouseLockY
        mouseLocked = True
        glutSetCursor(GLUT_CURSOR_NONE)
        mouseLockX = pmouseX
        mouseLockY = pmouseY

    def unlockMouse():
        global mouseLocked, pmouseX, pmouseY, mouseLockX, mouseLockY
        if mouseLocked:
            pyautogui.moveRel(mouseLockX-pmouseX, mouseLockY - pmouseY)
        mouseLocked = False
        glutSetCursor(GLUT_CURSOR_INHERIT)
        

    def windowWidth():
        global windowWidth
        return windowWidth

    def windowHeight():
        global windowHeight
        return windowHeight

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

