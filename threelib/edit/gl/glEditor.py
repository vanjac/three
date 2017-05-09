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
        print("OpenGL 1 Editor")
        super().__init__(mapPath, state)
        self.graphicsTools = GLGraphicsTools()

        self.fov = 60 # field of view
        self.nearClip = 0.1
        self.farClip = 2048.0

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
                                 self.editorMain.windowWidth() / 2)
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


        glPopMatrix()


        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)

        self._drawMiniAxes(rotate)
        if self.editorMain.windowWidth() > self.toolbarWidth:
            self._updateToolbar()
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


    def _drawStatusBar(self):
        glViewport(0, 0,
                   self.editorMain.windowWidth(), self.editorMain.windowHeight())
        glScissor(0, 0, self.editorMain.windowWidth(), self.statusBarHeight)
        glClear(GL_COLOR_BUFFER_BIT)

        # text
        glColor(1,1,1)
        self.editorMain.drawText(self.getStatusBar(),
                                 GLUT_BITMAP_8_BY_13, 4, 4)
        self.editorMain.drawText(str(self.editorMain.getFps()) + " FPS",
                                 GLUT_BITMAP_9_BY_15,
                                 4, self.editorMain.windowHeight() - 19) # 4+15


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

                if o.getMesh() is not None:
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

                if o.getMesh() is not None:
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
        g = int(index / 256) % 256
        b = int(index / (256**2)) % 256
        return float(r) / 256.0, float(g) / 256.0, float(b) / 256.0

    def subObjectIndexToColor(self, objectIndex, subIndex):
        objectIndex = int(objectIndex) + 1
        r = int(subIndex) % 256
        g = objectIndex % 256
        b = int(objectIndex / 256) % 256
        return float(r) / 256.0, float(g) / 256.0, float(b) / 256.0

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

        bg = button.style.background
        fg = button.style.foreground

        x1 = float(button.x) * self.toolbarWidth
        width = float(button.width) * self.toolbarWidth
        x2 = x1 + width

        y1 = y - height
        y2 = y

        enabled = button.enabled
        if self.currentCommand != "":
            buttonCommand = button.keyboardShortcut
            if not (buttonCommand == self.currentCommand
                    or buttonCommand.startswith(self.currentCommand)
                    or self.currentCommand.startswith(buttonCommand)):
                enabled = False
        if button == self.toolbarSelectButton:
            enabled = True

        hover = False
        if self.toolbarSelectButton is None and enabled and \
                (not (self.currentCommand != ""
                     and self.currentCommand.startswith(buttonCommand))) \
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
