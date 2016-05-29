__author__ = "vantjac"

from threelib.vectorMath import Vector
from collections import namedtuple

# vertex is a MeshVertex
# textureVertex is a Vector
MeshFaceVertex = namedtuple("MeshFaceVertex", ["vertex", "textureVertex"])


class MeshVertex:

    def __init__(self, position):
        self.v = position
        self.references = [ ] # list of MeshFaces that reference this vertex

    def getPosition(self):
        return self.v

    def setPosition(self, position):
        self.position = position

    # reference methods shouldn't be called directly

    def addReference(self, face):
        if face not in self.references:
            self.references.append(face)

    def removeReference(self, face):
        if face in self.references:
            self.references.remove(face)

    def numReferences(self):
        return len(self.references)

    def getReferences(self):
        return self.references

    def clearReferences(self):
        self.references = [ ]


class MeshFace:
    
    def __init__(self):
        # a list of MeshFaceVertex's
        self.vertices = [ ]
        self.material = None
        self.textureShift = Vector(0, 0)
        self.textureScale = Vector(0, 0)
        self.textureRotate = 0

    def getVertices(self):
        return self.vertices

    # return this MeshFace
    # for easy chaining of addVertex commands
    def addVertex(self, meshVertex, textureVertex=Vector(0,0), index=None):
        v = MeshFaceVertex(vertex=meshVertex, textureVertex=textureVertex)
        if index == None:
            self.vertices.append(v)
        else:
            self.vertices.insert(index, v)
        meshVertex.addReference(self)
        return self

    def removeVertex(self, meshFaceVertex):
        if meshFaceVertex in self.vertices:
            self.vertices.remove(meshFaceVertex)
        meshFaceVertex.removeReference(self)

    def replaceVertex(self, old, new):
        index = self.vertices.index(old)
        self.vertices[index] = new

    def setVertex(self, meshFaceVertex, meshVertex):
        v = MeshFaceVertex(vertex=meshVertex,
                           textureVertex = meshFaceVertex.textureVertex)
        self.replaceVertex(meshFaceVertex, v)

    def setTextureVertex(self, meshFaceVertex, textureVertex):
        v = MeshFaceVertex(vertex=meshFaceVertex.vertex,
                           textureVertex = textureVertex)
        self.replaceVertex(meshFaceVertex, v)

    def clearVertices(self):
        for v in self.vertices:
            v.removeReference(face)
        self.vertices = [ ]
    
    def setTextureTransform(self, shift, rotate, scale):
        self.textureShift = shift
        self.textureRotate = rotate
        self.textureScale = scale


class Mesh:
    
    def __init__(self):
        self.vertices = [ ] # list of MeshVertex's
        self.faces = [ ] # list of MeshFace's

    def getVertices(self):
        return self.vertices

    def addVertex(self, vertex=MeshVertex(Vector(0,0,0))):
        vertex.clearReferences()
        self.vertices.append(vertex)
        return vertex
    
    # if removeFaces is True, all faces that this vertex references will also
    # be removed. Setting this to False could be dangerous!
    def removeVertex(self, vertex, removeFaces=True):
        if removeFaces:
            faces = [ ]
            for face in vertex.getReferences():
                faces.append(face)
            for face in faces:
                self.removeFace(face)
        self.vertices.remove(vertex)

    def getFaces(self):
        return self.faces

    def addFace(self, face=MeshFace()):
        self.faces.append(face)
        for v in face.getVertices():
            v.addReference(face)
        return face

    # removing the face deletes all of its vertices
    # it is useless after that.
    def removeFace(self, face):
        self.faces.remove(face)
        face.clearVertices()
