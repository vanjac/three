__author__ = "vantjac"

import math

from threelib.edit.base import EditorObject
from threelib.vectorMath import *
from threelib.mesh import *

import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.GLU import *


class PointObject(EditorObject):
    
    def __init__(self):
        EditorObject.__init__(self)
        self.position = Vector(0, 0, 0)
        self.rotation = Rotate(0, 0, 0)
        self.baseRotation = Rotate(0, 0, 0)
        
    def getType(self):
        return "Point"

    def getPosition(self):
        return self.position
    
    def getRotation(self):
        return self.rotation
    
    def getBounds(self):
        return (Vector(0, 0, 0), Vector(0, 0, 0))

    def setPosition(self, position):
        self.position = position

    def setRotation(self, rotation):
        self.rotation = rotation

    def applyRotation(self):
        self.baseRotation.rotate(self.rotation)
        self.rotation = Rotate(0, 0, 0)

    def scale(self, factor):
        pass

    def getMesh(self):
        return None
    
    def drawObject(self):
        self.drawSelectHull((1.0, 1.0, 1.0))
    
    def drawSelectHull(self, color):
        glColor(color[0], color[1], color[2])
        glPointSize(10)
        glBegin(GL_POINTS)
        pos = self.position
        glVertex(pos.y, pos.z, pos.x)
        glEnd()
    
    def getProperties(self):
        return super().getProperties()

    def setProperties(self, properties):
        super().setProperties(properties)

    def clone(self):
        clone = PointObject()
        self.addToClone(clone)
        return clone
    
    def addToClone(self, clone):
        super().addToClone(clone)


class MeshObject(EditorObject):

    # starts as a cube
    # scale is the size of the cube / 2
    def __init__(self, scale=1):
        EditorObject.__init__(self)
        self.position = Vector(0, 0, 0)
        self.rotation = Rotate(0, 0, 0)
        self.mesh = Mesh()
        a = self.mesh.addVertex(MeshVertex(Vector(-scale, -scale, -scale)))
        b = self.mesh.addVertex(MeshVertex(Vector( scale, -scale, -scale)))
        c = self.mesh.addVertex(MeshVertex(Vector(-scale,  scale, -scale)))
        d = self.mesh.addVertex(MeshVertex(Vector( scale,  scale, -scale)))
        e = self.mesh.addVertex(MeshVertex(Vector(-scale, -scale,  scale)))
        f = self.mesh.addVertex(MeshVertex(Vector( scale, -scale,  scale)))
        g = self.mesh.addVertex(MeshVertex(Vector(-scale,  scale,  scale)))
        h = self.mesh.addVertex(MeshVertex(Vector( scale,  scale,  scale)))
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
        return "Mesh"

    def getPosition(self):
        return self.position
    
    def getRotation(self):
        return self.rotation
    
    def getBounds(self):
        firstVertexPos = self.mesh.getVertices()[0].getPosition()
        lowX = firstVertexPos.x
        lowY = firstVertexPos.y
        lowZ = firstVertexPos.z
        highX = firstVertexPos.x
        highY = firstVertexPos.y
        highZ = firstVertexPos.z
        for v in self.mesh.getVertices():
            pos = v.getPosition()
            if pos.x < lowX:
                lowX = pos.x
            if pos.x > highX:
                highX = pos.x
            if pos.y < lowY:
                lowY = pos.y
            if pos.y > highY:
                highY = pos.y
            if pos.z < lowZ:
                lowZ = pos.z
            if pos.z > highZ:
                highZ = pos.z
        return ( Vector(lowX, lowY, lowZ), Vector(highX, highY, highZ) )

    def setPosition(self, position):
        self.position = position

    def setRotation(self, rotation):
        self.rotation = rotation

    def applyRotation(self):
        for v in self.mesh.getVertices():
            v.setPosition(v.getPosition().rotate(self.rotation))
        self.rotation = Rotate(0, 0, 0)

    def scale(self, factor):
        for v in self.mesh.getVertices():
            v.setPosition(v.getPosition() * factor)

    def getMesh(self):
        return self.mesh

    def setMesh(self, mesh):
        self.mesh = mesh
    
    def drawObject(self):
        glColor(0.8, 0.8, 0.8)
        for f in self.mesh.getFaces():
            texture = False

            mat = f.getMaterial()
            if mat != None:
                if len(mat.material.texture) != 0:
                    texture = True
                    glEnable(GL_TEXTURE_2D)
                    glBindTexture(GL_TEXTURE_2D, mat.getNumber())
            
            glBegin(GL_POLYGON)
            for v in f.getVertices():
                pos = v.vertex.getPosition()
                texPos = v.textureVertex
                glTexCoord(texPos.x, texPos.y)
                glVertex(pos.y, pos.z, pos.x)
            glEnd()

            if texture:
                glDisable(GL_TEXTURE_2D)
    
    def drawSelectHull(self, color):
        glColor(color[0], color[1], color[2])
        for f in self.mesh.getFaces():
            glBegin(GL_POLYGON)
            for v in f.getVertices():
                pos = v.vertex.getPosition()
                glVertex(pos.y, pos.z, pos.x)
            glEnd()
    
    def getProperties(self):
        return super().getProperties()

    def setProperties(self, properties):
        super().setProperties(properties)

    def clone(self):
        clone = MeshObject()
        self.addToClone(clone)
        return clone
    
    def addToClone(self, clone):
        super().addToClone(clone)
        clone.setMesh(self.mesh.clone())
