__author__ = "vantjac"

import math

from threelib.edit.ui.editorUI import EditorUI
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


class GLEditor(EditorUI):
    
    def __init__(self, editorMain, state=None):
        super().__init__(editorMain, state)
        self.graphicsTools = GLGraphicsTools()

    def keyPressed(self, key, mouseX, mouseY):
        self.keyPressedEvent(key)

    def keyReleased(self, key, mouseX, mouseY):
        self.keyReleasedEvent(key)
        
    # mouse buttons: left=0, middle=1, right=2, 
    #   scroll-up=3, scroll-down=4, scroll-left=5, scroll-right=6
    def mousePressed(self, button, mouseX, mouseY):
        self.mousePressedEvent(button, mouseX, mouseY)
        
    def mouseReleased(self, button, mouseX, mouseY):
        self.mouseReleasedEvent(button, mouseX, mouseY)
    
    def mouseMoved(self, mouseX, mouseY, pmouseX, pmouseY):
        self.mouseMovedEvent(mouseX, mouseY, pmouseX, pmouseY)
    
    def init(self):
        glPolygonStipple(stipplePattern)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1) # for getting select pixels
                                              # and storing textures
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)

    def draw(self):
        for m in self.state.world.getAddedMaterials():
            print("Sending", m.getName(), "to OpenGL... ", end="")

            material = m.material

            texName = glGenTextures(1)
            m.setNumber(texName)
            
            glBindTexture(GL_TEXTURE_2D, texName);
            
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, 
                            GL_NEAREST);
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, 
                            GL_NEAREST);
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, material.getXLen(), 
                         material.getYLen(), 0, GL_RGBA, GL_UNSIGNED_BYTE, 
                         material.getTexture());
            print("Done")

        for m in self.state.world.getUpdatedMaterials():
            print("Updating and sending", m.getName(), "to OpenGL... ", end="")

            material = m.material
            texName = m.getNumber()
            
            glBindTexture(GL_TEXTURE_2D, texName);
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, material.getXLen(), 
                         material.getYLen(), 0, GL_RGBA, GL_UNSIGNED_BYTE, 
                         material.getTexture());
            print("Done")
        
        for m in self.state.world.getRemovedMaterials():
            texName = m.getNumber()
            glDeleteTextures([texName])

        glPushMatrix()
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
            elif drawVertices:
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
        # end select at cursor

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
                if o.getMesh() != None:
                    # a green point is used for the origin
                    glColor(0.0, 1.0, 0.0)
                    glPointSize(12)
                    glBegin(GL_POINTS)
                    glVertex(0, 0, 0)
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
                                 GLUT_BITMAP_9_BY_15, 4, 4)
        self.editorMain.drawText(str(self.editorMain.getFps()) + " FPS",
                                 GLUT_BITMAP_9_BY_15,
                                 4, self.editorMain.windowHeight() - 19) # 4+15
        
        self.drawMiniAxes(rotate)

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

    def drawMiniAxes(self, cameraRotate):
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
        glRotate(math.degrees(cameraRotate.x), 0, 0, 1)
        glRotate(math.degrees(cameraRotate.y), -1, 0, 0)
        glRotate(math.degrees(cameraRotate.z), 0, 1, 0)
        
        glBegin(GL_LINES)
        # x axis
        glColor(1.0, 0.0, 0.0)
        glVertex(0.0, 0.0, 0.0)
        glVertex(0.0, 0.0, 0.5)
        # y axis
        glColor(0.0, 1.0, 0.0)
        glVertex(0.0, 0.0, 0.0)
        glVertex(0.5, 0.0, 0.0)
        # z axis
        glColor(0.0, 0.0, 1.0)
        glVertex(0.0, 0.0, 0.0)
        glVertex(0.0, 0.5, 0.0)
        
        glEnd()

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

