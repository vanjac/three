__author__ = "vantjac"

import math

from threelib.edit.editorActions import EditorActions
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


class Editor(EditorActions):
    
    def __init__(self, editorMain, state=None):
        EditorActions.__init__(self, editorMain, state)

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
            self.saveFile()
            return True
        
        if c[0] == '\b':
            self.deleteSelected()
            return True

        if c[0] == 'm':
            if len(c) == 1:
                return False
            if c[1] == 'o':
                self.selectMode(EditorState.SELECT_OBJECTS)
                return True
            if c[1] == 'f':
                self.selectMode(EditorState.SELECT_FACES)
                return True
            if c[1] == 'v':
                self.selectMode(EditorState.SELECT_VERTICES)
                return True

        if c[0] == 'a':
            self.selectAll()
            return True

        if c[0] == 'g':
            self.translateSelected()
            return True
            
        if c[0] == 'r':
            self.rotateSelected()
            return True

        # if no match
        print("Unrecognized command " + c)
        return True

    def evaluateAdjustCommand(self, c):
        
        if c[0] == 'x':
            self.selectAdjustAxis(EditorActions.X)
            return True
        if c[0] == 'y':
            self.selectAdjustAxis(EditorActions.Y)
            return True
        if c[0] == 'z':
            self.selectAdjustAxis(EditorActions.Z)
            return True

        if c[0] == '[':
            self.multiplyGrid(0.5)
            return True
        if c[0] == ']':
            self.multiplyGrid(2.0)
            return True
        if c[0] == 's':
            self.toggleSnap()
            return True
        if c[0] == 'a':
            self.snapToGrid()
            return True
        if c[0] == 'o':
            self.adjustToOrigin()
            return True
        if c[0] == 'r':
            self.toggleRelativeCoordinates()
            return True
        if c[0].isdigit() or c[0] == '.' or c[0] == '-':
            if c[-1].isdigit() or c[-1] == '.' or c[-1] == '-':
                return False
            axisChar = c[-1].lower()
            try:
                number = float(c[:-1])
            except ValueError:
                print("Invalid command", c)
                return True
            if axisChar == 'x':
                self.setAdjustAxisValue(EditorActions.X, number)
            elif axisChar == 'y':
                self.setAdjustAxisValue(EditorActions.Y, number)
            elif axisChar == 'z':
                self.setAdjustAxisValue(EditorActions.Z, number)
            else:
                print("Invalid command", c)
            return True
        # if no match
        print("Unrecognized command", c)
        return True
        
    # mouse buttons: left=0, middle=1, right=2, 
    #   scroll-up=3, scroll-down=4, scroll-left=5, scroll-right=6
    def mousePressed(self, button, mouseX, mouseY):
        if button == 0:
            if self.inAdjustMode:
                self.inAdjustMode = False
                print("Complete adjust")
                self.editorMain.unlockMouse()
            else: # select
                multiple = self.editorMain.shiftPressed()
                self.selectAtCursor(multiple)
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
            mouseGrid = self.adjustMouseGrid
            value = list(self.adjustor.getAxes())
            axes = self.selectedAxes
            if axes[0] > axes[1]: # put axes in order
                axes = (axes[1], axes[0])
            if self.state.snapEnabled:
                mouseMovement = list(self.adjustMouseMovement)
                mouseMovement[0] += mouseX - pmouseX
                mouseMovement[1] += mouseY - pmouseY
                if mouseMovement[0] > mouseGrid:
                    value[axes[0]] += math.floor(mouseMovement[0] / mouseGrid)\
                                      * grid
                    mouseMovement[0] %= mouseGrid
                if mouseMovement[0] < -mouseGrid:
                    value[axes[0]] -= math.floor(-mouseMovement[0] / mouseGrid)\
                                      * grid
                    mouseMovement[0] = -(-mouseMovement[0] % mouseGrid)
                if mouseMovement[1] > mouseGrid:
                    value[axes[1]] += math.floor(mouseMovement[1] / mouseGrid)\
                                      * grid
                    mouseMovement[1] %= mouseGrid
                if mouseMovement[1] < -mouseGrid:
                    value[axes[1]] -= math.floor(-mouseMovement[1] / mouseGrid)\
                                      * grid
                    mouseMovement[1] = -(-mouseMovement[1] % mouseGrid)
                self.adjustMouseMovement = tuple(mouseMovement)
            else:
                mouseXChange = float(mouseX - pmouseX) / float(mouseGrid) * grid
                mouseYChange = float(mouseY - pmouseY) / float(mouseGrid) * grid
                value[axes[0]] += mouseXChange
                value[axes[1]] += mouseYChange
            self.adjustor.setAxes(tuple(value))


    def init(self):
        glPolygonStipple(stipplePattern)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1) # for getting select pixels

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
        
        if self.selectAtCursorOnDraw:
            self.selectAtCursorOnDraw = False
            self.drawSelectHulls()
            glFlush()
            glFinish()
            # gl y coordinates start at bottom of window
            pixels = glReadPixels(self.editorMain.mouseX(),
                                  self.editorMain.windowHeight() \
                                  - self.editorMain.mouseY(),
                                  1, 1, # width, height
                                  GL_RGB, GL_UNSIGNED_BYTE)
            color = (pixels[0], pixels[1], pixels[2])
            if self.state.selectMode == EditorState.SELECT_OBJECTS:
                index = self.colorToObjectIndex(color)
                if not self.selectMultiple:
                    self.state.deselectAll()
                if index != -1:
                    o = self.state.objects[index]
                    if o in self.state.selectedObjects:
                        self.state.deselect(o)
                    else:
                        self.state.select(o)
            elif self.state.selectMode == EditorState.SELECT_VERTICES:
                objectIndex, vertexIndex = self.colorToSubObjectIndex(color)
                if not self.selectMultiple:
                    self.state.selectedVertices = [ ]
                if objectIndex != -1:
                    editorObject = self.state.objects[objectIndex]
                    vertex = editorObject.getMesh().getVertices()[vertexIndex]
                    alreadySelected = False
                    for v in self.state.selectedVertices:
                        if v.vertex == vertex:
                            alreadySelected = True
                            self.state.selectedVertices.remove(v)
                            break
                    if not alreadySelected:
                        self.state.selectedVertices.append(
                            VertexSelection(editorObject, vertex))
            elif self.state.selectMode == EditorState.SELECT_FACES:
                objectIndex, faceIndex = self.colorToSubObjectIndex(color)
                if not self.selectMultiple:
                    self.state.selectedFaces = [ ]
                if objectIndex != -1:
                    editorObject = self.state.objects[objectIndex]
                    face = editorObject.getMesh().getFaces()[faceIndex]
                    alreadySelected = False
                    for f in self.state.selectedFaces:
                        if f.face == face:
                            alreadySelected = True
                            self.state.selectedFaces.remove(f)
                            break
                    if not alreadySelected:
                        self.state.selectedFaces.append(
                            FaceSelection(editorObject, face))
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # draw axes
        glBegin(GL_LINES)
        # x axis
        glColor(1.0, 0.0, 0.0)
        glVertex(0.0, 0.0, 0.0)
        glVertex(0.0, 0.0, 128.0)
        # y axis
        glColor(0.0, 1.0, 0.0)
        glVertex(0.0, 0.0, 0.0)
        glVertex(128.0, 0.0, 0.0)
        # z axis
        glColor(0.0, 0.0, 1.0)
        glVertex(0.0, 0.0, 0.0)
        glVertex(0.0, 128.0, 0.0)
        
        glEnd()
        
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
            glEnable(GL_POLYGON_OFFSET_FILL)
            glPolygonOffset(-0.75, -1.0)
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
            glDisable(GL_POLYGON_OFFSET_FILL)

    def drawSelectHulls(self):
        if self.state.selectMode == EditorState.SELECT_OBJECTS:
            i = 0
            for o in self.state.objects:
                glPushMatrix()
                self.transformObject(o)
                o.drawSelectHull(self.objectIndexToColor(i))
                glPopMatrix()
                i += 1
        elif self.state.selectMode == EditorState.SELECT_VERTICES:
            glPointSize(8)
            i = 0
            for o in self.state.objects:
                glPushMatrix()
                self.transformObject(o)
                
                # block selecting vertices through objects
                o.drawSelectHull((0, 0, 0))

                if o.getMesh != None:
                    glBegin(GL_POINTS)
                    j = 0
                    for v in o.getMesh().getVertices():
                        color = self.subObjectIndexToColor(i, j)
                        glColor(color[0], color[1], color[2])
                        pos = v.getPosition()
                        glVertex(pos.y, pos.z, pos.x)
                        j += 1
                    glEnd()

                glPopMatrix()
                i += 1
        elif self.state.selectMode == EditorState.SELECT_FACES:
            i = 0
            for o in self.state.objects:
                glPushMatrix()
                self.transformObject(o)
                
                if o.getMesh != None:
                    j = 0
                    for f in o.getMesh().getFaces():
                        glBegin(GL_POLYGON)
                        color = self.subObjectIndexToColor(i, j)
                        glColor(color[0], color[1], color[2])
                        for vertex in f.getVertices():
                            pos = vertex.vertex.getPosition()
                            glVertex(pos.y, pos.z, pos.x)
                        glEnd()
                        j += 1
                
                glPopMatrix()
                i += 1
            
    def transformObject(self, editorObject):
        oTranslate = editorObject.getPosition()
        oRotate = editorObject.getRotation()
        glTranslate(oTranslate.y, oTranslate.z, oTranslate.x)
        glRotate(math.degrees(oRotate.z), 0, 1, 0)
        glRotate(math.degrees(oRotate.y), -1, 0, 0)
        glRotate(math.degrees(oRotate.x), 0, 0, 1)

    def objectIndexToColor(self, index):
        index = int(index) + 1
        r = index % 256
        g = int(index / 256) % 256
        b = int(index / (256**2)) % 256
        return (float(r)/256.0, float(g)/256.0, float(b)/256.0)

    def subObjectIndexToColor(self, objectIndex, subIndex):
        objectIndex = int(objectIndex) + 1
        r = int(subIndex) % 256
        g = objectIndex % 256
        b = int(objectIndex / 256) % 256
        return (float(r)/256.0, float(g)/256.0, float(b)/256.0)

    # return -1 for no object
    def colorToObjectIndex(self, color):
        r = int(color[0])
        g = int(color[1])
        b = int(color[2])
        return b*(256**2) + g*256 + r - 1

    # returns a tuple of (objectIndex, subIndex)
    # objectIndex is -1 for nothing selected
    def colorToSubObjectIndex(self, color):
        r = int(color[0])
        g = int(color[1])
        b = int(color[2])
        return b*256 + g - 1, r
