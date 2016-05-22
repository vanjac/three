__author__ = "vantjac"

import math

from threelib.edit.state import EditorState
from threelib.vectorMath import Vector
from threelib.vectorMath import Rotate

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

class Editor:

    def __init__(self, editorMain):
        self.state = EditorState()
        self.editorMain = editorMain
        self.movingCamera = False
        self.lookSpeed = 1.0/100.0
        self.flySpeed = 1.0/10.0
        self.fly = Vector(0, 0, 0) # each component can be 0, 1, or -1

    def keyPressed(self, key, mouseX, mouseY):
        if key == b'w':
            if self.movingCamera:
                self.fly = self.fly.setX(-1)
        if key == b's':
            if self.movingCamera:
                self.fly = self.fly.setX(1)
        if key == b'a':
            if self.movingCamera:
                self.fly = self.fly.setY(-1)
        if key == b'd':
            if self.movingCamera:
                self.fly = self.fly.setY(1)
        if key == b'q':
            if self.movingCamera:
                self.fly = self.fly.setZ(-1)
        if key == b'e':
            if self.movingCamera:
                self.fly = self.fly.setZ(1)
        

    def keyReleased(self, key, mouseX, mouseY):
        if key == b'w':
            if self.movingCamera:
                self.fly = self.fly.setX(0)
        if key == b's':
            if self.movingCamera:
                self.fly = self.fly.setX(0)
        if key == b'a':
            if self.movingCamera:
                self.fly = self.fly.setY(0)
        if key == b'd':
            if self.movingCamera:
                self.fly = self.fly.setY(0)
        if key == b'q':
            if self.movingCamera:
                self.fly = self.fly.setZ(0)
        if key == b'e':
            if self.movingCamera:
                self.fly = self.fly.setZ(0)
        
    # mouse buttons: left=0, middle=1, right=2, 
    #   scroll-up=3, scroll-down=4, scroll-left=5, scroll-right=6
    def mousePressed(self, button, mouseX, mouseY):
        if button == 2:
            if self.movingCamera:
                self.movingCamera = False
                self.fly = Vector(0, 0, 0)
            else:
                self.movingCamera = True
        pass
        
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
        
        glTranslate(0, 0, -5)
        glBegin(GL_TRIANGLES)
        glColor(1.0, 0.0, 0.0)
        glVertex(0.0, 1.0, 0.0)
        glColor(0.0, 1.0, 0.0)
        glVertex(1.0, -1.0, 0.0)
        glColor(0.0, 0.0, 1.0)
        glVertex(-1.0, -1.0, 0.0)
        glEnd()