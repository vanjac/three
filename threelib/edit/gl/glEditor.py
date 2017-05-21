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

    VERTEX_SIZE = 8
    EDGE_WIDTH = 6

    SELECT_MAX_VERTICES = 8388608
    SELECT_MAX_EDGES_PER_VERTEX = 64

    def __init__(self, mapPath, state=None):
        print("OpenGL 1 Editor")
        super().__init__(mapPath, state)
        self.graphicsTools = GLGraphicsTools()

        self.fov = 60 # field of view
        self.nearClip = 0.1
        self.farClip = 2048.0

        if 'camera' in self.gameConfig:
            if 'fov' in self.gameConfig['camera']:
                self.fov = float(self.gameConfig['camera']['fov'])
            if 'nearclip' in self.gameConfig['camera']:
                self.nearClip = float(self.gameConfig['camera']['nearclip'])
            if 'farclip' in self.gameConfig['camera']:
                self.farClip = float(self.gameConfig['camera']['farclip'])

    def init(self):
        self._fullscreenMessage("Loading...")
        self._resetProjection()

        glPolygonStipple(stipplePattern)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1) # for getting select pixels
                                              # and storing textures
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)

        # initialize display lists
        self.drawAxesList = self.makeDisplayList()
        self.drawAxes()
        glEndList()

        glEnable(GL_SCISSOR_TEST)

    def _fullscreenMessage(self, message):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glColor(1, 1, 1)
        self.editorMain.drawText(message, GLUT_BITMAP_9_BY_15,
                                 self.editorMain.windowWidth() / 2,
                                 self.editorMain.windowHeight() / 2)
        glFlush()
        glFinish()
        glutSwapBuffers()

    def makeDisplayList(self):
        l = glGenLists(1)
        if not glIsList(l):
            print("Error making display list!")
            return None
        else:
            glNewList(l, GL_COMPILE)
            return l

    def resized(self):
        self._resetProjection()

    def _getViewportAspect(self):
        if self.editorMain.windowWidth() == self.toolbarWidth:
            return 1.0
        if self.editorMain.windowWidth() < self.toolbarWidth:
            return self.editorMain.getAspect()
        return (self.editorMain.windowWidth() - self.toolbarWidth) \
               / self.editorMain.windowHeight()

    # should be called if any settings like aspect
    # ratio, fov, near/far clip planes, have changed.
    def _resetProjection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, self._getViewportAspect(),
                       self.nearClip, self.farClip)
        glMatrixMode(GL_MODELVIEW)

    def draw(self):
        self.editorMain.updateMaterials(self.state.world)

        glLoadIdentity() # reset the view
        if self.editorMain.windowWidth() > self.toolbarWidth:
            glViewport(0, 0,
                       self.editorMain.windowWidth() - self.toolbarWidth,
                       self.editorMain.windowHeight())
            glScissor(0, 0,
                       self.editorMain.windowWidth() - self.toolbarWidth,
                       self.editorMain.windowHeight())
        else:
            glViewport(0, 0,
                       self.editorMain.windowWidth(),
                       self.editorMain.windowHeight())
            glScissor(0, 0,
                      self.editorMain.windowWidth(),
                      self.editorMain.windowHeight())

        # clear screen and depth buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

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

        # draw create position
        createPos = self.state.createPosition
        glColor(1.0, 0.0, 1.0)
        glPointSize(14)
        glBegin(GL_POINTS)
        glVertex(createPos.y, createPos.z, createPos.x)
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

                # a green line is used for the direction
                glColor(0.0, 1.0, 0.0)
                glBegin(GL_LINES)
                glVertex(0, 0, 0)
                glVertex(0, 0, 32)
                glEnd()

                if o.getMesh() is not None:
                    # a green point is used for the origin
                    glPointSize(12)
                    glBegin(GL_POINTS)
                    glVertex(0, 0, 0)
                    glEnd()

                # a magenta line is drawn to the parent object
                if o.getParent() is not None:
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

            if drawVertices and o.getMesh() is not None:
                # red points are used for vertices
                glColor(1.0, 0.0, 0.0)
                glPointSize(GLEditor.VERTEX_SIZE)
                glBegin(GL_POINTS)
                for v in o.getMesh().getVertices():
                    pos = v.getPosition()
                    glVertex(pos.y, pos.z, pos.x)
                glEnd()

                # red lines are used for edges
                for f in o.getMesh().getFaces():
                    glLineWidth(GLEditor.EDGE_WIDTH)
                    glBegin(GL_LINE_LOOP)
                    for v in f.getVertices():
                        pos = v.vertex.getPosition()
                        glVertex(pos.y, pos.z, pos.x)
                    glEnd()
                    glLineWidth(1)

            glPopMatrix()
        # end for each object

        if drawVertices:
            glColor(1.0, 1.0, 1.0)
            glPointSize(GLEditor.VERTEX_SIZE + 2)
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


        glPopMatrix()


        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)

        self._drawFPS()
        self._drawMiniAxes(rotate)
        if self.editorMain.windowWidth() > self.toolbarWidth:
            self._drawToolbar()
        self._drawStatusBar()

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)


    def _drawMiniAxes(self, rotate):
        glPushMatrix()

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glTranslate(0.7, -0.85, 0)
        glScale(1.0 / self._getViewportAspect(), 1, 1)
        gluPerspective(self.fov, 1, 4, 16)
        glMatrixMode(GL_MODELVIEW)

        glTranslate(0, 0, -5)
        glRotate(math.degrees(rotate.x), 0, 0, 1)
        glRotate(math.degrees(rotate.y), -1, 0, 0)
        glRotate(math.degrees(rotate.z), 0, 1, 0)
        glScale(0.5, 0.5, 0.5)

        glCallList(self.drawAxesList)

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def _drawFPS(self):
        glColor(1,1,1)
        self.editorMain.drawText(str(self.editorMain.getFps()) + " FPS",
                                 GLUT_BITMAP_9_BY_15,
                                 4, self.editorMain.windowHeight() - 19)  # 4+15

    def _drawStatusBar(self):
        glViewport(0, 0,
                   self.editorMain.windowWidth(), self.editorMain.windowHeight())
        glScissor(0, 0, self.editorMain.windowWidth(), self.statusBarHeight)
        glClear(GL_COLOR_BUFFER_BIT)

        # text
        glColor(1,1,1)
        self.editorMain.drawText(self.getStatusBar(),
                                 GLUT_BITMAP_8_BY_13, 4, 4)
        self.editorMain.drawText(self.printMessage,
                                 GLUT_BITMAP_8_BY_13, 4, 20)


    def _readSelectPixel(self):
        glFlush()
        glFinish()
        # gl y coordinates start at bottom of window
        pixels = glReadPixels(self.editorMain.mouseX(),
                              self.editorMain.windowHeight() \
                              - self.editorMain.mouseY() - 1,
                              1, 1,  # width, height
                              GL_RGB, GL_UNSIGNED_BYTE)
        # uncomment to show select colors
        # glutSwapBuffers()
        # import time
        # time.sleep(2)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        return pixels[0], pixels[1], pixels[2]


    def cursorSelect(self):
        self.selectAtCursorOnDraw = False
        if self.state.selectMode == EditorState.SELECT_OBJECTS:
            o = self.selectObject()
            if not self.selectMultiple:
                self.state.deselectAll()
            if o is not None:
                if o in self.state.selectedObjects:
                    self.state.deselect(o)
                else:
                    self.state.select(o)
        elif self.state.selectMode == EditorState.SELECT_VERTICES:
            editorObject, vertices = self.selectVertex()
            if not self.selectMultiple:
                self.state.selectedVertices = [ ]
            for vertex in vertices:
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
            editorObject, face = self.selectFace()
            if not self.selectMultiple:
                self.state.selectedFaces = [ ]
            if face is not None:
                alreadySelected = False
                for f in self.state.selectedFaces:
                    if f.face == face:
                        alreadySelected = True
                        self.state.selectedFaces.remove(f)
                        break
                if not alreadySelected:
                    self.state.selectedFaces.append(
                        FaceSelection(editorObject, face))

    # return the object at the cursor
    # if self.selectBehindSelection, ignores selected objects
    def selectObject(self):
        self.drawObjectSelectHulls(self.selectBehindSelection)
        color = self._readSelectPixel()
        index = self.colorToObjectIndex(color)
        if index == -1:
            return None
        return self.state.objects[index]

    # return editorObject, face
    def selectFace(self):
        editorObject = self.selectObject()
        if editorObject == None:
            return None, None
        objectHasSelectedFaces = False
        for face in self.state.selectedFaces:
            if face.editorObject == editorObject:
                objectHasSelectedFaces = True

        self.drawFaceSelectHulls(editorObject, self.selectBehindSelection)
        color = self._readSelectPixel()
        faceIndex = self.colorToObjectIndex(color)
        if faceIndex == -1:
            if objectHasSelectedFaces and self.selectBehindSelection:
                # hide object and try again
                self.state.select(editorObject)
                ret = self.selectFace()
                self.state.deselect(editorObject)
                return ret
            else:
                return None, None
        return editorObject, editorObject.getMesh().getFaces()[faceIndex]

    # return editorObject, list of vertices
    def selectVertex(self):
        self.drawObjectFrameSelectHulls(self.selectBehindSelection)
        color = self._readSelectPixel()
        objectIndex = self.colorToObjectIndex(color)
        if objectIndex == -1:
            return None, [ ]
        editorObject = self.state.objects[objectIndex]
        objectHasSelectedVertices = False
        for vertex in self.state.selectedVertices:
            if vertex.editorObject == editorObject:
                objectHasSelectedVertices = True
        vertices = editorObject.getMesh().getVertices()

        self.drawVertexSelectHulls(editorObject, self.selectBehindSelection)
        color = self._readSelectPixel()
        vertexIndex = self.colorToObjectIndex(color)
        if vertexIndex == -1:
            if objectHasSelectedVertices and self.selectBehindSelection:
                # hide object and try again
                self.state.select(editorObject)
                ret = self.selectVertex()
                self.state.deselect(editorObject)
                return ret
            else:
                return None, [ ]

        edge = False
        if vertexIndex >= GLEditor.SELECT_MAX_VERTICES:
            edge = True
            vertexIndex -= GLEditor.SELECT_MAX_VERTICES
        if edge:
            vertexFaceIndex = vertexIndex % GLEditor.SELECT_MAX_EDGES_PER_VERTEX
            vertexIndex //= GLEditor.SELECT_MAX_EDGES_PER_VERTEX
            v2 = vertices[vertexIndex]
            face = v2.getReferences()[vertexFaceIndex]
            v2Index = face.indexOf(v2)
            v1 = face.getVertices()[v2Index - 1].vertex
            return editorObject, [v1, v2]
        else:
            return editorObject, [vertices[vertexIndex]]


    def drawObjectSelectHulls(self, behindSelection=False):
        i = 0
        for o in self.state.objects:
            if behindSelection and o.isSelected():
                i += 1
                continue
            glPushMatrix()
            self.transformObject(o)
            o.drawSelectHull(self.objectIndexToColor(i), self.graphicsTools)
            glPopMatrix()
            i += 1

    # vertices and edges
    def drawObjectFrameSelectHulls(self, behindSelection=False):
        if behindSelection:
            selectedVertices = [ ]
            for v in self.state.selectedVertices:
                selectedVertices.append(v.vertex)
        glPointSize(GLEditor.VERTEX_SIZE)
        i = 0
        for o in self.state.objects:
            color = self.objectIndexToColor(i)

            glPushMatrix()
            self.transformObject(o)

            # block selecting vertices through objects
            o.drawSelectHull((0, 0, 0), self.graphicsTools)

            if o.getMesh() is not None:
                vertices = o.getMesh().getVertices()

                # edges
                glLineWidth(GLEditor.EDGE_WIDTH)
                for f in o.getMesh().getFaces():
                    for j in range(0, len(f.getVertices())):
                        v1 = f.getVertices()[j - 1].vertex
                        v2 = f.getVertices()[j].vertex
                        if behindSelection and v1 in selectedVertices \
                                and v2 in selectedVertices:
                            continue
                        glColor(color[0], color[1], color[2])
                        glBegin(GL_LINES)
                        pos = v1.getPosition()
                        glVertex(pos.y, pos.z, pos.x)
                        pos = v2.getPosition()
                        glVertex(pos.y, pos.z, pos.x)
                        glEnd()
                glLineWidth(1)
                # vertex points
                glBegin(GL_POINTS)
                for v in vertices:
                    if behindSelection and v in selectedVertices:
                        continue
                    glColor(color[0], color[1], color[2])
                    pos = v.getPosition()
                    glVertex(pos.y, pos.z, pos.x)
                glEnd()

            glPopMatrix()
            i += 1

    def drawVertexSelectHulls(self, editorObject, behindSelection=False):
        if behindSelection:
            selectedVertices = [ ]
            for v in self.state.selectedVertices:
                selectedVertices.append(v.vertex)
        glPointSize(GLEditor.VERTEX_SIZE)
        glPushMatrix()
        self.transformObject(editorObject)

        # block selecting vertices through objects
        editorObject.drawSelectHull((0, 0, 0), self.graphicsTools)

        if editorObject.getMesh() is not None:
            vertices = editorObject.getMesh().getVertices()

            # edges
            glLineWidth(GLEditor.EDGE_WIDTH)
            for f in editorObject.getMesh().getFaces():
                for i in range(0, len(f.getVertices())):
                    v1 = f.getVertices()[i - 1].vertex
                    v2 = f.getVertices()[i].vertex
                    if behindSelection and v1 in selectedVertices \
                            and v2 in selectedVertices:
                        continue
                    v2Index = vertices.index(v2)
                    vertexFaceIndex = v2.getReferences().index(f)
                    edgeId = vertexFaceIndex \
                             + v2Index * GLEditor.SELECT_MAX_EDGES_PER_VERTEX
                    color = self.objectIndexToColor(
                        edgeId + GLEditor.SELECT_MAX_VERTICES)
                    glColor(color[0], color[1], color[2])
                    glBegin(GL_LINES)
                    pos = v1.getPosition()
                    glVertex(pos.y, pos.z, pos.x)
                    pos = v2.getPosition()
                    glVertex(pos.y, pos.z, pos.x)
                    glEnd()
            glLineWidth(1)
            # vertex points
            glBegin(GL_POINTS)
            i = 0
            for v in vertices:
                if behindSelection and v in selectedVertices:
                    i += 1
                    continue
                color = self.objectIndexToColor(i)
                glColor(color[0], color[1], color[2])
                pos = v.getPosition()
                glVertex(pos.y, pos.z, pos.x)
                i += 1
            glEnd()

        glPopMatrix()

    def drawFaceSelectHulls(self, editorObject, behindSelection=False):
        if behindSelection:
            selectedFaces = [ ]
            for f in self.state.selectedFaces:
                selectedFaces.append(f.face)
        glPushMatrix()
        self.transformObject(editorObject)

        if editorObject.getMesh() is not None:
            i = 0
            for f in editorObject.getMesh().getFaces():
                if behindSelection and f in selectedFaces:
                    i += 1
                    continue
                glBegin(GL_POLYGON)
                color = self.objectIndexToColor(i)
                glColor(color[0], color[1], color[2])
                for vertex in f.getVertices():
                    pos = vertex.vertex.getPosition()
                    glVertex(pos.y, pos.z, pos.x)
                glEnd()
                i += 1

        glPopMatrix()


    # display list
    def drawAxes(self):
        glLineWidth(4)
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
        glLineWidth(1)


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
        g = int(index // 256) % 256
        b = int(index // 65536) % 256
        return float(r) / 255.0, float(g) / 255.0, float(b) / 255.0

    # return -1 for no object
    def colorToObjectIndex(self, color):
        r = int(color[0])
        g = int(color[1])
        b = int(color[2])
        return b*65536 + g*256 + r - 1


    def _drawToolbar(self):
        self.toolbarHoverButton = None

        glViewport(self.editorMain.windowWidth() - self.toolbarWidth, 0,
                   self.toolbarWidth, self.editorMain.windowHeight())
        glScissor(self.editorMain.windowWidth() - self.toolbarWidth, 0,
                   self.toolbarWidth, self.editorMain.windowHeight())

        glClear(GL_COLOR_BUFFER_BIT)

        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, self.toolbarWidth, 0, self.editorMain.windowHeight())

        y = self.editorMain.windowHeight() + self.toolbarScroll
        yStart = y

        for group in self.toolbarGroups:
            if not group.shown:
                continue
            glColor(255,255,255)
            glRasterPos(4, y - 20)
            for c in group.name:
                glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ctypes.c_int(ord(c)))
            y -= 28

            for row in group.rows:
                for button in row.buttons:
                    self._drawButton(button, y, row.height)
                y -= row.height

        self.toolbarHeight = yStart - y
        if y > self.statusBarHeight:
            self.toolbarScroll -= y - self.statusBarHeight
            if self.toolbarScroll < 0:
                self.toolbarScroll = 0

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

    def _drawButton(self, button, y, height):
        command = self.currentCommand
        if self.inAdjustMode:
            command = ""

        bg = button.style.background
        fg = button.style.foreground

        x1 = float(button.x) * self.toolbarWidth
        width = float(button.width) * self.toolbarWidth
        x2 = x1 + width

        y1 = y - height
        y2 = y

        enabled = button.enabled
        buttonCommand = button.keyboardShortcut
        if command != "":
            if not (buttonCommand == command
                    or buttonCommand.startswith(command)
                    or command.startswith(buttonCommand)):
                enabled = False
        if button == self.toolbarSelectButton:
            enabled = True

        hover = False
        if self.toolbarSelectButton is None and enabled and \
                (not (command != ""
                     and command.startswith(buttonCommand))) \
                and x1 < self.toolbarMouseX < x2 \
                and y1 < self.toolbarMouseY < y2:
            hover = True
            self.toolbarHoverButton = button

        if bg is not None:
            if not enabled:
                bg = (63, 63, 63)
                fg = (0, 0, 0)
            elif button == self.toolbarSelectButton:
                bg = tuple([max(0, c - 63) for c in bg])
            elif hover:
                bg = tuple([min(255.0, 255 - (255 - c) / 2) for c in bg])

            glColor(bg[0] / 255, bg[1] / 255, bg[2] / 255)
            glBegin(GL_QUADS)
            glVertex(x1, y1)
            glVertex(x1, y2)
            glVertex(x2, y2)
            glVertex(x2, y1)
            glEnd()

        glColor(fg[0] / 255, fg[1] / 255, fg[2] / 255)
        glBegin(GL_LINE_LOOP)
        glVertex(x1, y1)
        glVertex(x1, y2)
        glVertex(x2, y2)
        glVertex(x2, y1)
        glEnd()

        textWidth = 9 * len(button.text)
        glRasterPos(x1 + width/2 - textWidth/2, y1 + height/2 - 4)
        for c in button.text:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ctypes.c_int(ord(c)))
