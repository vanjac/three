__author__ = "vantjac"

import math

from threelib.edit.base import EditorObject
from threelib.vectorMath import *
from threelib.mesh import *

from threelib.sim.graphics import RenderMesh


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
    
    def drawObject(self, graphicsTools):
        if self.isSelected():
            graphicsTools.drawPoint(Vector(0,0,0), (0.0, 1.0, 1.0), 12)
        else:
            graphicsTools.drawPoint(Vector(0,0,0), (1.0, 1.0, 1.0), 12)
    
    def drawSelectHull(self, color, graphicsTools):
        graphicsTools.drawPoint(Vector(0,0,0), color, 10)
    
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
        clone.setRotation(self.baseRotation)
        clone.applyRotation()
        clone.setRotation(self.rotation)


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
        if len(self.mesh.getVertices()) == 0:
            return (Vector(0, 0, 0), Vector(0, 0, 0))
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
    
    def drawObject(self, graphicsTools):
        graphicsTools.drawMesh(self.mesh)
    
    def drawSelectHull(self, color, graphicsTools):
        graphicsTools.drawMeshSelectHull(self.mesh, color)
    
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
      
        
class SolidMeshObject(MeshObject):

    def __init__(self, scale=1):
        super().__init__(scale)
        self.blockUseables = True
        self.visible = True
        self.useAction = ""
    
    def addToWorld(self, world):
        renderMesh = RenderMesh(self.getMesh())
        world.renderMeshes.append(renderMesh)
        
    def getProperties(self):
        props = super().getProperties()
        props.update({ "blockUseables" : str(self.blockUseables),
                       "visible" : str(self.visible),
                       "useAction" : self.useAction
                     })
        return props
        
    def setProperties(self, properties):
        super().setProperties(properties)
        for key, value in properties.items():
            if key == "blockUseables":
                self.blockUseables = value.lower() == "true"
            if key == "visible":
                self.visible = value.lower() == "true"
            if key == "useAction":
                self.useAction = value

