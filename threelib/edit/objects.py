__author__ = "vantjac"

import math

from threelib.edit.state import EditorObject
from threelib.vectorMath import *

from OpenGL.GL import *
from OpenGL.GLU import *

class TestObject(EditorObject):

    def __init__(self):
        EditorObject.__init__(self)
        self.name = "Test"
        self.position = Vector(-5, 0, 0)
        self.rotation = Rotate(0, math.radians(30), math.radians(30))
        
    def getType(self):
        return "Test"

    def getPosition(self):
        return self.position
    
    def getRotation(self):
        return self.rotation
    
    def getBounds(self):
        pass

    def setPosition(self, position):
        self.position = position

    def setRotation(self, rotation):
        self.rotation = rotation

    def setScale(self, scale):
        pass

    def getMesh(self):
        pass
    
    def drawObject(self):
        glBegin(GL_TRIANGLES)
        glColor(1.0, 0.0, 0.0)
        glVertex(0.0, 1.0, 0.0)
        glColor(0.0, 1.0, 0.0)
        glVertex(1.0, -1.0, 0.0)
        glColor(0.0, 0.0, 1.0)
        glVertex(-1.0, -1.0, 0.0)
        glEnd()
    
    def drawSelectHull(self, color):
        pass
    
    def getProperties(self):
        pass

    def setProperties(self):
        pass
