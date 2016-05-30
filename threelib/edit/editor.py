__author__ = "vantjac"

import math

from threelib.edit.state import *
from threelib.vectorMath import Vector
from threelib.vectorMath import Rotate
from threelib.edit.objects import *
from threelib.edit.adjust import *

from threelib import files

from OpenGL.GL import *
from OpenGL.GLU import *


stipplePattern = [
    0xAA, 0xAA, 0xAA, 0xAA, 0x55, 0x55, 0x55, 0x55, 
    0xAA, 0xAA, 0xAA, 0xAA, 0x55, 0x55, 0x55, 0x55, 
    0xAA, 0xAA, 0xAA, 0xAA, 0x55, 0x55, 0x55, 0x55,
    0xAA, 0xAA, 0xAA, 0xAA, 0x55, 0x55, 0x55, 0x55, 
    0xAA, 0xAA, 0xAA, 0xAA, 0x55, 0x55, 0x55, 0x55, 
    0xAA, 0xAA, 0xAA, 0xAA, 0x55, 0x55, 0x55, 0x55,
    0xAA, 0xAA, 0xAA, 0xAA, 0x55, 0x55, 0x55, 0x55, 
    0xAA, 0xAA, 0xAA, 0xAA, 0x55, 0x55, 0x55, 0x55, 
    0xAA, 0xAA, 0xAA, 0xAA, 0x55, 0x55, 0x55, 0x55,
    0xAA, 0xAA, 0xAA, 0xAA, 0x55, 0x55, 0x55, 0x55, 
    0xAA, 0xAA, 0xAA, 0xAA, 0x55, 0x55, 0x55, 0x55, 
    0xAA, 0xAA, 0xAA, 0xAA, 0x55, 0x55, 0x55, 0x55,
    0xAA, 0xAA, 0xAA, 0xAA, 0x55, 0x55, 0x55, 0x55, 
    0xAA, 0xAA, 0xAA, 0xAA, 0x55, 0x55, 0x55, 0x55, 
    0xAA, 0xAA, 0xAA, 0xAA, 0x55, 0x55, 0x55, 0x55,
    0xAA, 0xAA, 0xAA, 0xAA, 0x55, 0x55, 0x55, 0x55 ]


class Editor:
    
    X = 0
    Y = 1
    Z = 2
    
    def __init__(self, editorMain, state=None):
        if state == None:
            self.state = EditorState()
        else:
            self.state = state
        self.editorMain = editorMain
        self.currentCommand = ""
        self.movingCamera = False
        self.lookSpeed = .005
        self.flySpeed = 1.0/10.0
        self.fly = Vector(0, 0, 0) # each component can be 0, 1, or -1

        # adjust mode
        self.inAdjustMode = False
        self.adjustor = None
        self.adjustorOriginalValue = (0.0, 0.0, 0.0)
        self.selectedAxes = (Editor.X, Editor.Y)
        self.adjustMouseMovement = (0, 0)
        self.adjustMouseGrid = 16 # number of pixels per grid line
        
        # test code
        if len(self.state.objects) == 0:
            testObject = TestObject()
            self.state.objects.append(testObject)
            self.state.select(testObject)

    def keyPressed(self, key, mouseX, mouseY):
        if key[0] == 27: # escape
            print("Escape")
            self.currentCommand = ""
            self.movingCamera = False
            self.fly = Vector(0, 0, 0)
            self.editorMain.unlockMouse()
            if self.inAdjustMode:
                self.adjustor.setAxes(self.adjustorOriginalValue)
                self.inAdjustMode = False
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
            clearCommand = False
            if self.inAdjustMode:
                clearCommand = self.evaluateAdjustCommand(self.currentCommand)
            else:
                clearCommand = self.evaluateCommand(self.currentCommand)
            if clearCommand:
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

        if c[0] == '`': #save
            print("Saving map... ", end="")
            files.saveMapState(files.getCurrentMap(), self.state)
            print("Done")
            return True
        
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
                self.state.deselectAll()
            return True

        if c[0] == 'm':
            if len(c) == 1:
                return False
            if c[1] == 'o':
                print("Object select mode")
                self.state.selectMode = EditorState.SELECT_OBJECTS
                self.state.deselectAll()
                self.state.selectedVertices = [ ]
                self.state.selectedFaces = [ ]
                return True
            if c[1] == 'f':
                print("Face select mode")
                self.state.selectMode = EditorState.SELECT_FACES
                self.state.deselectAll()
                self.state.selectedVertices = [ ]
                self.state.selectedFaces = [ ]
                return True
            if c[1] == 'v':
                print("Vertex select mode")
                self.state.selectMode = EditorState.SELECT_VERTICES
                self.state.deselectAll()
                self.state.selectedVertices = [ ]
                self.state.selectedFaces = [ ]
                return True

        if c[0] == 'a':
            if self.state.selectMode == EditorState.SELECT_OBJECTS:
                if len(self.state.selectedObjects) == 0:
                    self.state.selectAll()
                    print("Select", len(self.state.selectedObjects), "objects")
                else:
                    self.state.deselectAll()
                    print("Select none")
            elif self.state.selectMode == EditorState.SELECT_FACES:
                if len(self.state.selectedFaces) == 0:
                    for o in self.state.objects:
                        if o.getMesh() != None:
                            for f in o.getMesh().getFaces():
                                self.state.selectedFaces.append(
                                    FaceSelection(o, f))
                    print("Select", len(self.state.selectedFaces), "faces")
                else:
                    self.state.selectedFaces = [ ]
                    print("Select none")
            elif self.state.selectMode == EditorState.SELECT_VERTICES:
                if len(self.state.selectedVertices) == 0:
                    for o in self.state.objects:
                        if o.getMesh() != None:
                            for v in o.getMesh().getVertices():
                                self.state.selectedVertices.append(
                                    VertexSelection(o, v))
                    print("Select", len(self.state.selectedVertices),
                          "vertices")
                else:
                    self.state.selectedVertices = [ ]
                    print("Select none")
            
            return True

        if c[0] == 'g':
            print("Grab")
            self.setupAdjustMode(TestAdjustor())
            return True
            

        # if no match
        print("Unrecognized command " + c)
        return True

    def evaluateAdjustCommand(self, c):
        
        if c[0] == 'x':
            print("Select X axis")
            self.selectedAxes = (self.selectedAxes[1], Editor.X)
            return True
        if c[0] == 'y':
            print("Select Y axis")
            self.selectedAxes = (self.selectedAxes[1], Editor.Y)
            return True
        if c[0] == 'z':
            print("Select Z axis")
            self.selectedAxes = (self.selectedAxes[1], Editor.Z)
            return True

        if c[0] == '[':
            gridType = self.adjustor.gridType()
            self.state.setGridSize(gridType, \
                                   self.state.getGridSize(gridType) / 2.0)
            print("Grid size:", self.state.getGridSize(gridType))
            return True
        if c[0] == ']':
            gridType = self.adjustor.gridType()
            self.state.setGridSize(gridType, \
                                   self.state.getGridSize(gridType) * 2.0)
            print("Grid size:", self.state.getGridSize(gridType))
            return True
        

        # if no match
        print("Unrecognized command " + c)
        return True

    def setupAdjustMode(self, adjustor):
        self.inAdjustMode = True
        self.adjustor = adjustor
        self.adjustorOriginalValue = adjustor.getAxes()
        self.adjustMouseMovement = (0, 0)
        self.editorMain.lockMouse()
        
    # mouse buttons: left=0, middle=1, right=2, 
    #   scroll-up=3, scroll-down=4, scroll-left=5, scroll-right=6
    def mousePressed(self, button, mouseX, mouseY):
        if button == 0:
            if self.inAdjustMode:
                self.inAdjustMode = False
                print("Confirm adjust")
                self.editorMain.unlockMouse()
        if button == 2:
            if self.movingCamera:
                self.movingCamera = False
                self.fly = Vector(0, 0, 0)
                if not self.inAdjustMode:
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
        elif self.inAdjustMode:
            grid = float(self.state.getGridSize(self.adjustor.gridType()))
            mouseXChange = float(mouseX - pmouseX) \
                           / float(self.adjustMouseGrid) * grid
            mouseYChange = float(mouseY - pmouseY) \
                           / float(self.adjustMouseGrid) * grid
            axes = self.selectedAxes
            if axes[0] > axes[1]: # put axes in order
                axes = (axes[1], axes[0])
            value = list(self.adjustor.getAxes())
            value[axes[0]] += mouseXChange
            value[axes[1]] += mouseYChange
            self.adjustor.setAxes(tuple(value))


    def init(self):
        glPolygonStipple(stipplePattern)

    def draw(self):
        rotate = self.state.cameraRotation
        translate = self.state.cameraPosition
        glRotate(math.degrees(rotate.x), 0, 0, 1)
        glRotate(math.degrees(rotate.y), -1, 0, 0)
        glRotate(math.degrees(rotate.z), 0, 1, 0)
        glTranslate(translate.y, translate.z, translate.x)

        self.state.cameraPosition += (-self.fly * self.flySpeed).rotate(
            -self.state.cameraRotation)
        
        drawVertices = self.state.selectMode == EditorState.SELECT_VERTICES
        
        for o in self.state.objects:
            glPushMatrix()
            self.transformObject(o)
            
            select = o.isSelected()
            if select:
                glEnable(GL_POLYGON_STIPPLE)
            o.drawObject()
            if select:
                glDisable(GL_POLYGON_STIPPLE)

            if drawVertices and o.getMesh != None:
                glColor(1.0, 0.0, 0.0)
                glPointSize(8)
                glBegin(GL_POINTS)
                for v in o.getMesh().getVertices():
                    pos = v.getPosition()
                    glVertex(pos.y, pos.z, pos.x)
                glEnd()

            glPopMatrix()

        if drawVertices:
            glColor(1.0, 1.0, 1.0)
            glPointSize(10)
            for vSelect in self.state.selectedVertices:
                glPushMatrix()
                self.transformObject(vSelect.editorObject)
                pos = vSelect.vertex.getPosition()
                glBegin(GL_POINTS)
                glVertex(pos.y, pos.z, pos.x)
                glEnd()
                glPopMatrix()

        if self.state.selectMode == EditorState.SELECT_FACES:
            glColor(0.0, 0.0, 1.0)
            glEnable(GL_POLYGON_STIPPLE)
            for fSelect in self.state.selectedFaces:
                glPushMatrix()
                self.transformObject(fSelect.editorObject)
                glBegin(GL_POLYGON)
                for vertex in fSelect.face.getVertices():
                    pos = vertex.vertex.getPosition()
                    glVertex(pos.y, pos.z, pos.x)
                glEnd()
                glPopMatrix()
            glDisable(GL_POLYGON_STIPPLE)
            
    def transformObject(self, editorObject):
        oTranslate = editorObject.getPosition()
        oRotate = editorObject.getRotation()
        glTranslate(oTranslate.y, oTranslate.z, oTranslate.x)
        glRotate(math.degrees(oRotate.z), 0, 1, 0)
        glRotate(math.degrees(oRotate.y), -1, 0, 0)
        glRotate(math.degrees(oRotate.x), 0, 0, 1)
