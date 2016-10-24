__author__ = "jacobvanthoog"

from threelib.app import AppInterface
from threelib.app import AppInstance

import time # for fps
import threading # for pyautogui mouse movement

import pyautogui

import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


mouseMovementLock = threading.Lock()


class GLAppInstance(AppInstance):
    
    # pass in an EditorState to initialize the Editor with that state
    def __init__(self, appInterface, flags):
        # Global projection settings
        # Call resetProjection() if any of these are changed
        self.aspect = 1 # aspect ratio of the window (width / height)
        self.width = 1024
        self.height = 736
        self.fov = 60 # field of view
        self.nearClip = 4
        self.farClip = 2048.0

        # Mouse info
        self.mouseButtonPressed = [ False for i in range(0, 7) ]
        self.pmouseX = 0
        self.pmouseY = 0
        self.mouseLocked = False
        # position mouse was locked at
        self.mouseLockX = 0
        self.mouseLockY = 0

        self.mouseLockMargin = 64
        self.framesSinceMouseLockMove = 0

        # Keyboard info
        self.keysPressed = [ ]

        self.lastFpsTime = time.time()
        self.fpsCount = 0
        self.fps = 0
        
        self.appInterface = appInterface
        appInterface.setAppInstance(self)\
        
        # OpenGL Init:
        
        # pass arguments to init
        glutInit(sys.argv)
        
        # Select type of display mode:   
        #  Double buffer 
        #  RGBA color
        #  Alpha components supported 
        #  Depth buffer
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)

        glutInitWindowSize(self.width, self.height)
        glutInitWindowPosition(0, 0)
        
        # Retain window id to use when closing
        # global variable
        window = glutCreateWindow(b'three') # must be byte string
        
        print("Using OpenGL version:", glGetString(GL_VERSION).decode())
        
        # Uncomment this line to get full screen.
        #glutFullScreen()
        
        # Register important functions
        glutDisplayFunc(self.drawGL)
        glutIdleFunc(self.drawGL)
        glutReshapeFunc(self.resizeGL)
        glutKeyboardFunc(self.keyPressedEvent)
        glutKeyboardUpFunc(self.keyReleasedEvent)
        glutMouseFunc(self.mouseEvent)
        # called while no mouse buttons are pressed
        glutPassiveMotionFunc(self.mouseMovement)
        # called while mouse buttons are pressed
        glutMotionFunc(self.mouseMovement)

        glutIgnoreKeyRepeat(True)
        
        # Initialize the window. 
        self.initGL(self.width, self.height)
        
        # Start Event Processing Engine	
        glutMainLoop()
    

    def getFps(self):
        return self.fps

    def windowWidth(self):
        return self.width

    def windowHeight(self):
        return self.height

    def getAspect(self):
        return self.aspect

    def getFOV(self):
        return self.fov

    def buttonPressed(self, button=0):
        return self.mouseButtonPressed[button]

    def shiftPressed(self):
        return glutGetModifiers() & GLUT_ACTIVE_SHIFT

    def ctrlPressed(self):
        return glutGetModifiers() & GLUT_ACTIVE_CTRL

    def altPressed(self):
        return glutGetModifiers() & GLUT_ACTIVE_CTRL

    def mouseX(self):
        return self.pmouseX

    def mouseY(self):
        return self.pmouseY

    def lockMouse(self):
        if not self.mouseLocked:
            self.mouseLockX = self.pmouseX
            self.mouseLockY = self.pmouseY
        self.mouseLocked = True
        glutSetCursor(GLUT_CURSOR_NONE)

    def unlockMouse(self):
        if self.mouseLocked:
            pyautogui.moveRel(self.mouseLockX - self.pmouseX,
                              self.mouseLockY - self.pmouseY)
        self.mouseLocked = False
        glutSetCursor(GLUT_CURSOR_INHERIT)


    # General OpenGL initialization function.
    def initGL(self, width, height):
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0) # enables clearing of depth buffer
        glDepthFunc(GL_LESS) # type of depth test to use
        glEnable(GL_DEPTH_TEST) # enable depth testing
        glShadeModel(GL_SMOOTH) # enable smooth color shading

        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
    
        self.width = width
        self.height = height
        self.resetProjection()

        # draw loading screen
        glColor(1,1,1)
        self.drawText("Loading...", GLUT_BITMAP_9_BY_15,
                              self.width / 2, self.height / 2)
        glFlush()
        glFinish()
        glutSwapBuffers()
        # done drawing loading screen

        self.appInterface.init()
    
    # Called when window is resized
    def resizeGL(self, width, height):
        if height == 0: # prevent divide by zero error 
            height = 1
    
        self.width = width
        self.height = height
        # reset the current viewport and perspective transformation
        glViewport(0, 0, width, height)
        self.resetProjection()

    # should be called if any settings like aspect
    # ratio, fov, near/far clip planes, have changed.
    def resetProjection(self):
        self.aspect = float(self.width) / float(self.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, self.aspect, self.nearClip, self.farClip)
        glMatrixMode(GL_MODELVIEW)
        
    # The main drawing function. 
    def drawGL(self):
        self.fpsCount += 1
        
        seconds = time.time()
        if seconds - self.lastFpsTime > 1:
            self.lastFpsTime = seconds
            self.fps = self.fpsCount
            self.fpsCount = 0

        # clear screen and depth buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity() # reset the view
        
        self.appInterface.draw()
        
        if glGetError() != GL_NO_ERROR:
            print("GL Error!")
        
        #  double buffered - swap the buffers to display what just got drawn. 
        glutSwapBuffers()

    # info passed as tuple: (button, eventType, mouseX, mouseY)
    # button: left=0, middle=1, right=2, 
    #   scroll-up=3, scroll-down=4, scroll-left=5, scroll-right=6
    # eventType: mousePressed=0, mouseReleased=1
    def mouseEvent(self, *args):
        button = args[0]
        pressed = args[1] == 0
        self.mouseButtonPressed[button] = pressed
        if pressed:
            self.appInterface.mousePressed(button, args[2], args[3])
        else:
            self.appInterface.mouseReleased(button, args[2], args[3])

    def mouseMovement(self, mouseX, mouseY):
        # ignore mouse movements created by locking
        if (abs(mouseX - self.pmouseX) > self.width / 2 
            or abs(mouseY - self.pmouseY) > self.height / 2):
            self.pmouseX = mouseX
            self.pmouseY = mouseY
            return

        self.appInterface.mouseMoved(mouseX, mouseY, self.pmouseX, self.pmouseY)
        self.framesSinceMouseLockMove += 1
        if self.mouseLocked and self.framesSinceMouseLockMove > 4:
            if mouseX > self.width - self.mouseLockMargin:
                def moveToLeft():
                    global mouseMovementLock
                    mouseMovementLock.acquire()
                    pyautogui.moveRel(-self.width
                        + 3 * self.mouseLockMargin, 0)
                    mouseMovementLock.release()
                # run in a separate thread to prevent frames being dropped
                threading.Thread(target=moveToLeft).start()
                self.framesSinceMouseLockMove = 0
            if mouseX < self.mouseLockMargin:
                def moveToRight():
                    global mouseMovementLock
                    mouseMovementLock.acquire()
                    pyautogui.moveRel(self.width
                        - 3 * self.mouseLockMargin, 0)
                    mouseMovementLock.release()
                threading.Thread(target=moveToRight).start()
                self.framesSinceMouseLockMove = 0
            if mouseY > self.height - self.mouseLockMargin:
                def moveToTop():
                    global mouseMovementLock
                    mouseMovementLock.acquire()
                    pyautogui.moveRel(0, -self.height
                        + 3 * self.mouseLockMargin)
                    mouseMovementLock.release()
                threading.Thread(target=moveToTop).start()
                self.framesSinceMouseLockMove = 0
            if mouseY < self.mouseLockMargin:
                def moveToBottom():
                    global mouseMovementLock
                    mouseMovementLock.acquire()
                    pyautogui.moveRel(0, self.height
                        - 3 * self.mouseLockMargin)
                    mouseMovementLock.release()
                threading.Thread(target=moveToBottom).start()
                self.framesSinceMouseLockMove = 0
        self.pmouseX = mouseX
        self.pmouseY = mouseY
        
    def keyPressedEvent(self, key, mouseX, mouseY):
        if key in self.keysPressed:
            # ignore key repeat
            pass
        else:
            self.keysPressed.append(key)
            self.appInterface.keyPressed(key)
        
    def keyReleasedEvent(self, key, mouseX, mouseY):
        if key in self.keysPressed:
            self.keysPressed.remove(key)
        self.appInterface.keyReleased(key)

    def drawText(self, text, font, x, y):
        depthEnabled = glIsEnabled(GL_DEPTH_TEST)
        glDisable(GL_DEPTH_TEST)
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0.0, self.width, 0.0, self.height)

        glRasterPos(x,y)
        for c in text :
            glutBitmapCharacter(font, ctypes.c_int(ord(c)))
        
        if depthEnabled:
            glEnable(GL_DEPTH_TEST)

        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        
    # gl-specific and three-specific functions:
    
    def updateMaterials(self, world):
        """
        Should be called every loop
        """
        for m in world.getAddedMaterials():
            m.setLoaded(True)
            texture = m.loadAlbedoTexture()
            texName = glGenTextures(1)
            m.setNumber(texName)
            
            # even if the texture was not loaded correctly, it might be
            # reloaded correctly in the future, so everything has to be set up
            glBindTexture(GL_TEXTURE_2D, texName);
            
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, 
                            GL_NEAREST);
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, 
                            GL_NEAREST);
            
            self.sendTexture(texture)

        for m in world.getUpdatedMaterials():
            m.setLoaded(True)
            texture = m.loadAlbedoTexture()
            texName = m.getNumber()
            
            glBindTexture(GL_TEXTURE_2D, texName);
            self.sendTexture(texture)
        
        for m in world.getRemovedMaterials():
            texName = m.getNumber()
            glDeleteTextures([texName])
    
    def sendTexture(self, texture):
        if texture != None:
            mode = texture.getDataType()
            print("Sending", mode, "texture to OpenGL...")

            if mode == "RGB":
                glMode = GL_RGB
            elif mode == "RGBA":
                glMode = GL_RGBA
            else:
                print("Unrecognized texture mode!")
                return
            
            glTexImage2D(GL_TEXTURE_2D, 0, glMode, texture.getXLen(), 
                         texture.getYLen(), 0, glMode, GL_UNSIGNED_BYTE, 
                         texture.getData())
            print("Done sending")

