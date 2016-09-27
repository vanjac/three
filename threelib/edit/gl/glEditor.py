__author__ = "jacobvanthoog"

import math

from threelib.edit.appInterface.editorInterface import EditorInterface
from threelib.edit.state import *
from threelib.vectorMath import Vector
from threelib.vectorMath import Rotate
from threelib.edit.objects import *
from threelib.edit.adjust import *

from threelib.edit.gl.glGraphics import GLGraphicsTools

import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

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


class GLEditor(EditorInterface):
    
    def __init__(self, mapPath, state=None):
        super().__init__(mapPath, state)
        self.graphicsTools = GLGraphicsTools()
        print("OpenGL 1 Editor")
    
    def init(self):
        glPolygonStipple(stipplePattern)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1) # for getting select pixels
                                              # and storing textures
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)

        # initialize display lists
        self.drawAxesList = self.makeDisplayList()
        self.drawAxes()
        glEndList()

        self.drawMiniAxesList1 = self.makeDisplayList()
        self.drawMiniAxes1()
        glEndList()

        self.drawMiniAxesList2 = self.makeDisplayList()
        self.drawMiniAxes2()
        glEndList()

    def makeDisplayList(self):
        l = glGenLists(1)
        if not glIsList(l):
            print("Error making display list!")
            return None
        else:
            glNewList(l, GL_COMPILE)
            return l

    def draw(self):
        self.editorMain.updateMaterials(self.state.world)

        glPushMatrix()
        rotate = self.state.cameraRotation
        translate = self.state.cameraPosition
        glRotate(math.degrees(rotate.x), 0, 0, 1)
        glRotate(math.degrees(rotate.y), -1, 0, 0)
        glRotate(math.degrees(rotate.z), 0, 1, 0)
        glTranslate(translate.y, translate.z, translate.x)
        
        fps = float(self.editorMain.getFps())
        if fps == 0:
            fps = 60
        self.state.cameraPosition += (-self.fly * self.flySpeed / fps) \
            .rotate(-self.state.cameraRotation)
        
        drawVertices = self.state.selectMode == EditorState.SELECT_VERTICES
        
        if self.selectAtCursorOnDraw:
            self.cursorSelect()

        glPushMatrix()
        glScale(128.0, 128.0, 128.0)
        glCallList(self.drawAxesList)
        glPopMatrix()

        # draw arrow
        if self.arrowShown:
            startPos = self.arrowStart
            endPos = self.arrowEnd
            glColor(1.0, 1.0, 1.0)
            glPointSize(12)

            glBegin(GL_POINTS)
            glVertex(startPos.y, startPos.z, startPos.x)
            glEnd()
            
            glBegin(GL_LINES)
            glVertex(startPos.y, startPos.z, startPos.x)
            glVertex(endPos.y, endPos.z, endPos.x)
            glEnd()
        
        for o in self.state.objects:
            glPushMatrix()
            self.transformObject(o)
            
            select = o.isSelected()
            if select:
                glEnable(GL_POLYGON_STIPPLE)
            
            o.drawObject(self.graphicsTools)
            
            if select:
                glDisable(GL_POLYGON_STIPPLE)
                
                # a green line is used for the direction
                glColor(0.0, 1.0, 0.0)
                glBegin(GL_LINES)
                glVertex(0, 0, 0)
                glVertex(0, 0, 32)
                glEnd()
                
                if o.getMesh() != None:
                    # a green point is used for the origin
                    glPointSize(12)
                    glBegin(GL_POINTS)
                    glVertex(0, 0, 0)
                    glEnd()
                
                # a magenta line is drawn to the parent object
                if o.getParent() != None:
                    glColor(1.0, 0.0, 1.0)
                    glBegin(GL_LINES)
                    glVertex(0, 0, 0)
                    parentPos = o.getParent().getPosition() - o.getPosition()
                    glVertex(parentPos.y, parentPos.z, parentPos.x)
                    glEnd()
                    
                # cyan lines are drawn to child objects
                if len(o.getChildren()) > 0:
                    glColor(0.0, 1.0, 1.0)
                    glBegin(GL_LINES)
                    for child in o.getChildren():
                        glVertex(0, 0, 0)
                        childPos = child.getPosition() - o.getPosition()
                        glVertex(childPos.y, childPos.z, childPos.x)
                    glEnd()

            if drawVertices and o.getMesh() != None:
                # red points are used for vertices
                glColor(1.0, 0.0, 0.0)
                glPointSize(8)
                glBegin(GL_POINTS)
                for v in o.getMesh().getVertices():
                    pos = v.getPosition()
                    glVertex(pos.y, pos.z, pos.x)
                glEnd()
                
                # red lines are used for edges
                for f in o.getMesh().getFaces():
                    glBegin(GL_LINE_LOOP)
                    for v in f.getVertices():
                        pos = v.vertex.getPosition()
                        glVertex(pos.y, pos.z, pos.x)
                    glEnd()
                
            glPopMatrix()
        # end for each object

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
        
        # status bar
        glColor(1,1,1)
        glPopMatrix()
        self.editorMain.drawText(self.getStatusBar(),
                                 GLUT_BITMAP_8_BY_13, 4, 4)
        self.editorMain.drawText(str(self.editorMain.getFps()) + " FPS",
                                 GLUT_BITMAP_9_BY_15,
                                 4, self.editorMain.windowHeight() - 19) # 4+15
        
        glCallList(self.drawMiniAxesList1)
        glRotate(math.degrees(rotate.x), 0, 0, 1)
        glRotate(math.degrees(rotate.y), -1, 0, 0)
        glRotate(math.degrees(rotate.z), 0, 1, 0)
        glCallList(self.drawMiniAxesList2)


    def cursorSelect(self):
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


    def drawSelectHulls(self):
        if self.state.selectMode == EditorState.SELECT_OBJECTS:
            i = 0
            for o in self.state.objects:
                glPushMatrix()
                self.transformObject(o)
                o.drawSelectHull(self.objectIndexToColor(i), self.graphicsTools)
                glPopMatrix()
                i += 1
        elif self.state.selectMode == EditorState.SELECT_VERTICES:
            glPointSize(8)
            i = 0
            for o in self.state.objects:
                glPushMatrix()
                self.transformObject(o)
                
                # block selecting vertices through objects
                o.drawSelectHull((0, 0, 0), self.graphicsTools)

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

    # display list
    def drawAxes(self):
        glBegin(GL_LINES)
        # x axis
        glColor(1.0, 0.0, 0.0)
        glVertex(0.0, 0.0, 0.0)
        glVertex(0.0, 0.0, 1.0)
        # y axis
        glColor(0.0, 1.0, 0.0)
        glVertex(0.0, 0.0, 0.0)
        glVertex(1.0, 0.0, 0.0)
        # z axis
        glColor(0.0, 0.0, 1.0)
        glVertex(0.0, 0.0, 0.0)
        glVertex(0.0, 1.0, 0.0)
        glEnd()

    # display list
    def drawMiniAxes1(self):
        glDisable(GL_DEPTH_TEST)
        glPushMatrix()

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glTranslate(0.7, -0.85, 0)
        glScale(1/self.editorMain.getAspect(), 1, 1)
        gluPerspective(self.editorMain.getFOV(), 1, 4, 16)
        glMatrixMode(GL_MODELVIEW)
        
        glTranslate(0, 0, -5)

    # display list
    def drawMiniAxes2(self):
        glScale(0.5, 0.5, 0.5)
        
        glCallList(self.drawAxesList)

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        glEnable(GL_DEPTH_TEST)
    
            
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

