__author__ = "vantjac"

import math

from threelib.edit.state import EditorObject
from threelib.vectorMath import *
from threelib.mesh import *

from OpenGL.GL import *
from OpenGL.GLU import *

class TestObject(EditorObject):

    def __init__(self):
        EditorObject.__init__(self)
        self.name = "Test"
        self.position = Vector(-5, 0, 0)
        self.rotation = Rotate(0, math.radians(30), math.radians(30))
        self.mesh = Mesh()
        a = self.mesh.addVertex(MeshVertex(Vector(-1, -1, -1)))
        b = self.mesh.addVertex(MeshVertex(Vector( 1, -1, -1)))
        c = self.mesh.addVertex(MeshVertex(Vector(-1,  1, -1)))
        d = self.mesh.addVertex(MeshVertex(Vector( 1,  1, -1)))
        e = self.mesh.addVertex(MeshVertex(Vector(-1, -1,  1)))
        f = self.mesh.addVertex(MeshVertex(Vector( 1, -1,  1)))
        g = self.mesh.addVertex(MeshVertex(Vector(-1,  1,  1)))
        h = self.mesh.addVertex(MeshVertex(Vector( 1,  1,  1)))
        top = self.mesh.addFace(MeshFace())
        front = self.mesh.addFace(MeshFace())
        right = self.mesh.addFace(MeshFace())
        bottom = self.mesh.addFace(MeshFace())
        back = self.mesh.addFace(MeshFace())
        left = self.mesh.addFace(MeshFace())
        top.addVertex(e).addVertex(f).addVertex(h).addVertex(g)
        front.addVertex(f).addVertex(b).addVertex(d).addVertex(h)
        right.addVertex(g).addVertex(h).addVertex(d).addVertex(c)
        bottom.addVertex(a).addVertex(c).addVertex(d).addVertex(b)
        back.addVertex(e).addVertex(g).addVertex(c).addVertex(a)
        left.addVertex(f).addVertex(e).addVertex(a).addVertex(b)
        
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

    def scale(self, factor):
        pass

    def getMesh(self):
        return self.mesh
    
    def drawObject(self):
        glBegin(GL_TRIANGLES)
        glColor(1.0, 0.0, 0.0)
        glVertex(0.0, 16.0, 0.0)
        glColor(0.0, 1.0, 0.0)
        glVertex(-16.0, -16.0, 0.0)
        glColor(0.0, 0.0, 1.0)
        glVertex(16.0, -16.0, 0.0)
        glEnd()
    
    def drawSelectHull(self, color):
        pass
    
    def getProperties(self):
        pass

    def setProperties(self):
        pass
