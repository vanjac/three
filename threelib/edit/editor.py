__author__ = "vantjac"

import math

from threelib.edit.state import EditorState
from threelib.vectorMath import Vector
from threelib.vectorMath import Rotate
from threelib.edit.objects import *

from OpenGL.GL import *
from OpenGL.GLU import *

class Editor:

    def __init__(self, editorMain):
        self.state = EditorState()
        self.editorMain = editorMain
        self.currentCommand = ""
        self.movingCamera = False
        self.lookSpeed = .005
        self.flySpeed = 1.0/10.0
        self.fly = Vector(0, 0, 0) # each component can be 0, 1, or -1

        # test code
        testObject = TestObject()
        self.state.objects.append(testObject)
        self.state.selectedObjects.append(testObject)

    def keyPressed(self, key, mouseX, mouseY):
        if key[0] == 27: # escape
            print("Escape")
            self.currentCommand = ""
            self.movingCamera = False
            self.fly = Vector(0, 0, 0)
            self.editorMain.unlockMouse()
        elif self.movingCamera:
            if key == b'w':
                self.fly = self.fly.setX(-1)
            if key == b's':
                self.fly = self.fly.setX(1)
            if key == b'a':
                self.fly = self.fly.setY(-1)
            if key == b'd':
                self.fly = self.fly.setY(1)
            if key == b'q':
                self.fly = self.fly.setZ(-1)
            if key == b'e':
                self.fly = self.fly.setZ(1)
        else:
            self.currentCommand += chr(key[0])
            if self.evaluateCommand(self.currentCommand):
                self.currentCommand = ""

    def keyReleased(self, key, mouseX, mouseY):
        if self.movingCamera:
            if key == b'w':
                self.fly = self.fly.setX(0)
            if key == b's':
                self.fly = self.fly.setX(0)
            if key == b'a':
                self.fly = self.fly.setY(0)
            if key == b'd':
                self.fly = self.fly.setY(0)
            if key == b'q':
                self.fly = self.fly.setZ(0)
            if key == b'e':
                self.fly = self.fly.setZ(0)

    # return True to clear current command
    def evaluateCommand(self, c):
        
        if c[0] == '\b':
            if self.state.selectMode == EditorState.SELECT_FACES:
                print("Faces cannot be deleted")
            elif self.state.selectMode == EditorState.SELECT_VERTICES:
                print("Vertices cannot be deleted")
            elif len(self.state.selectedObjects) == 0:
                print("Nothing selected")
            else:
                print("Delete selected objects")
                for o in self.state.selectedObjects:
                    o.removeFromParent()
                    self.state.objects.remove(o)
                self.state.selectedObjects = [ ]
            return True

        if c[0] == 'm':
            if len(c) == 1:
                return False
            if c[1] == 'o':
                print("Object select mode")
                self.state.selectMode = EditorState.SELECT_OBJECTS
                self.state.selectedObjects = [ ]
                return True
            if c[1] == 'f':
                print("Face select mode")
                self.state.selectMode = EditorState.SELECT_FACES
                self.state.selectedFaces = [ ]
                return True
            if c[1] == 'v':
                print("Vertex select mode")
                self.state.selectMode = EditorState.SELECT_VERTICES
                self.state.selectedVertices = [ ]
                return True

        # if no match
        print("Unrecognized command " + c)
        return True
        
    # mouse buttons: left=0, middle=1, right=2, 
    #   scroll-up=3, scroll-down=4, scroll-left=5, scroll-right=6
    def mousePressed(self, button, mouseX, mouseY):
        if button == 2:
            if self.movingCamera:
                self.movingCamera = False
                self.fly = Vector(0, 0, 0)
                self.editorMain.unlockMouse()
            else:
                self.movingCamera = True
                self.editorMain.lockMouse()
        if button == 3:
            self.flySpeed *= 1.1
        if button == 4:
            self.flySpeed /= 1.1
        
    def mouseReleased(self, button, mouseX, mouseY):
        pass
    
    def mouseMoved(self, mouseX, mouseY, pmouseX, pmouseY):
        if self.movingCamera:
            movement = Rotate(0,
                              -float(mouseY - pmouseY) * self.lookSpeed,
                              float(mouseX - pmouseX) * self.lookSpeed)
            self.state.cameraRotation += movement

    def draw(self):
        rotate = self.state.cameraRotation
        translate = self.state.cameraPosition
        glRotate(math.degrees(rotate.x), 0, 0, 1)
        glRotate(math.degrees(rotate.y), -1, 0, 0)
        glRotate(math.degrees(rotate.z), 0, 1, 0)
        glTranslate(translate.y, translate.z, translate.x)

        self.state.cameraPosition += (-self.fly * self.flySpeed).rotate(
            -self.state.cameraRotation)
        
        for o in self.state.objects:
            glPushMatrix()
            oTranslate = o.getPosition()
            oRotate = o.getRotation()
            glTranslate(oTranslate.y, oTranslate.z, oTranslate.x)
            glRotate(math.degrees(oRotate.z), 0, 1, 0)
            glRotate(math.degrees(oRotate.y), -1, 0, 0)
            glRotate(math.degrees(oRotate.x), 0, 0, 1)
            o.drawObject()
            glPopMatrix()
