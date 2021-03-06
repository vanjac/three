__author__ = "jacobvanthoog"

MANUAL_FRAMERATE_TIMING = False

from threelib.app import AppInterface
from threelib.app import AppInstance

import time # for fps
import threading # for pyautogui mouse movement

import pyautogui
# normally the failsafe exists as a way to stop pyautogui if you lose control.
# but we don't need that because this code is perfectly bug-free.
# what could possibly go wrong?
pyautogui.FAILSAFE = False

import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

mouseMovementLock = threading.Lock()


class GLAppInstance(AppInstance):

    def __init__(self, appInterface, flags):
        self.aspect = 1 # aspect ratio of the window (width / height)
        self.width = 1024
        self.height = 736

        # Mouse info
        self.mouseButtonPressed = [ False for i in range(0, 7) ]
        self.pmouseX = 0
        self.pmouseY = 0
        self.mouseLocked = False
        # position mouse was locked at
        self.mouseLockX = 0
        self.mouseLockY = 0

        self.mouseLockMargin = 192

        # Sometimes GLUT ignores the glutIgnoreKeyRepeat setting.
        # This keeps track of keys that are currently pressed, so multiple
        # keypress calls won't do anything.
        self.keysPressed = [ ]

        self.lastFpsTime = time.time()
        self.fpsCount = 0
        self.fps = 0

        self.appInterface = appInterface
        appInterface.setAppInstance(self)\

        # OpenGL Init:

        # pass arguments to init
        glutInit(sys.argv)

        # Specify type of display mode:
        #  RGBA color (alpha supported)
        #  Double buffer
        #  Depth buffer
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)

        glutInitWindowSize(self.width, self.height)
        glutInitWindowPosition(0, 0)

        glutCreateWindow(b'three') # must be byte string

        print("Using OpenGL version:", glGetString(GL_VERSION).decode())

        if "fullscreen" in flags:
            glutFullScreen()

        # Register event functions
        glutDisplayFunc(self.drawGL)
        if not MANUAL_FRAMERATE_TIMING:
            glutIdleFunc(self.drawGL)
        glutReshapeFunc(self.resizeGL)
        glutKeyboardFunc(self.keyPressedEvent)
        glutKeyboardUpFunc(self.keyReleasedEvent)
        glutSpecialFunc(self.specialPressedEvent)
        glutSpecialUpFunc(self.specialReleasedEvent)
        glutMouseFunc(self.mouseEvent)
        # called while no mouse buttons are pressed
        glutPassiveMotionFunc(self.mouseMovement)
        # called while mouse buttons are pressed
        glutMotionFunc(self.mouseMovement)
        glutEntryFunc(self.mouseEntryEvent)

        glutIgnoreKeyRepeat(True)

        # initialize the window
        self.initGL(self.width, self.height)

        # start main loop and event processing
        glutMainLoop()


    def getFps(self):
        return self.fps

    def windowWidth(self):
        return self.width

    def windowHeight(self):
        return self.height

    def getAspect(self):
        return self.aspect

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
            global mouseMovementLock
            self.mouseLocked = False
            pyautogui.moveTo(glutGet(GLUT_WINDOW_X) + self.mouseLockX,
                             glutGet(GLUT_WINDOW_Y) + self.mouseLockY)
            mouseMovementLock = threading.Lock()
        glutSetCursor(GLUT_CURSOR_INHERIT)

    def mouseIsLocked(self):
        return self.mouseLocked


    def initGL(self, width, height):
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0) # enables clearing of depth buffer
        glDepthFunc(GL_LESS) # type of depth test to use
        glEnable(GL_DEPTH_TEST) # enable depth testing
        glShadeModel(GL_SMOOTH) # enable smooth color shading

        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        self.appInterface.init()

        self.resizeGL(width, height)

    # Called when window is resized
    def resizeGL(self, width, height):
        if height == 0: # prevent divide by zero error
            height = 1

        self.width = width
        self.height = height
        self.aspect = float(self.width) / float(self.height)
        # reset the current viewport and perspective transformation
        glViewport(0, 0, width, height)

        self.appInterface.resized()

    # Draw loop
    def drawGL(self):
        self.fpsCount += 1

        seconds = time.time()
        if seconds - self.lastFpsTime > 1:
            self.lastFpsTime = seconds
            self.fps = self.fpsCount
            self.fpsCount = 0

        self.appInterface.draw()

        if glGetError() != GL_NO_ERROR:
            print("GL Error!")

        #  double buffered - swap the buffers to display what just got drawn.
        glutSwapBuffers()

        if MANUAL_FRAMERATE_TIMING:
            # call display again in 15 milliseconds
            glutTimerFunc(16, self.timer, 0)

    def timer(self, idNum):
        glutPostRedisplay()

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
        global mouseMovementLock

        # ignore mouse movements created by locking
        if abs(mouseX - self.pmouseX) > self.width / 2 \
                or abs(mouseY - self.pmouseY) > self.height / 2:
            pass
        else:
            self.appInterface.mouseMoved(mouseX, mouseY, self.pmouseX, self.pmouseY)
        self.pmouseX = mouseX
        self.pmouseY = mouseY

        if self.mouseLocked and \
                (mouseX < self.mouseLockMargin / 2
                or mouseX > self.width - self.mouseLockMargin / 2
                or mouseY < self.mouseLockMargin / 2
                or mouseY > self.height - self.mouseLockMargin / 2):
            self._wrapMouse()

    def mouseEntryEvent(self, state):
        if state == 0 and self.mouseLocked:
            self._wrapMouse()

    def _wrapMouse(self):
        windowX = glutGet(GLUT_WINDOW_X)
        windowY = glutGet(GLUT_WINDOW_Y)

        def moveMouse():
            global mouseMovementLock
            mouseMovementLock.acquire()

            if not self.mouseLocked:
                return

            newX = windowX + self.width / 2
            newY = windowY + self.height / 2
            if self.pmouseX > self.width // 2:
                newX = windowX + self.mouseLockMargin
            if self.pmouseX < self.width // 2:
                newX = windowX + self.width - self.mouseLockMargin
            if self.pmouseY > self.height // 2:
                newY = windowY + self.mouseLockMargin
            if self.pmouseY < self.height // 2:
                newY = windowY + self.height - self.mouseLockMargin

            pyautogui.moveTo(newX, newY)
            mouseMovementLock.release()

        # run in a separate thread to prevent frames being dropped
        threading.Thread(target=moveMouse).start()

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

    def _nameForSpecialKey(self, key):
        keyNames = {GLUT_KEY_LEFT : "left",
                GLUT_KEY_RIGHT : "right",
                GLUT_KEY_DOWN : "down",
                GLUT_KEY_UP : "up",
                GLUT_KEY_PAGE_UP : "page_up",
                GLUT_KEY_PAGE_DOWN : "page_down",
                GLUT_KEY_HOME : "home",
                GLUT_KEY_END : "end",
                GLUT_KEY_INSERT : "insert"}
        if key in keyNames:
            return keyNames[key]
        return None

    def specialPressedEvent(self, key, mouseX, mouseY):
        if key in self.keysPressed:
            # ignore key repeat
            pass
        else:
            self.keysPressed.append(key)
            self.appInterface.specialKeyPressed(self._nameForSpecialKey(key))

    def specialReleasedEvent(self, key, mouseX, mouseY):
        if key in self.keysPressed:
            self.keysPressed.remove(key)
        self.appInterface.specialKeyReleased(self._nameForSpecialKey(key))

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

    def clearMaterials(self, world):
        for m in world.materials:
            texName = m.getNumber()
            glDeleteTextures([texName])

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
            glBindTexture(GL_TEXTURE_2D, texName)

            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,
                            GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,
                            GL_NEAREST)

            self.sendTexture(texture)

        for m in world.getUpdatedMaterials():
            m.setLoaded(True)
            texture = m.loadAlbedoTexture()
            texName = m.getNumber()

            glBindTexture(GL_TEXTURE_2D, texName)
            self.sendTexture(texture)

        for m in world.getRemovedMaterials():
            texName = m.getNumber()
            glDeleteTextures([texName])

    def sendTexture(self, texture):
        if texture is not None:
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

