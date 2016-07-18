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

    def clone(self):
        return MeshVertex(self.v)

    def getPosition(self):
        return self.v

    def setPosition(self, position):
        self.v = position
        for face in self.references:
            face.calculateTextureVertices()

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
    def addVertex(self, meshVertex, textureVertex=None, index=None):
        calculate = False
        if textureVertex == None:
            textureVertex = Vector(0,0)
            calculate = True
        
        v = MeshFaceVertex(vertex=meshVertex, textureVertex=textureVertex)
        if index == None:
            self.vertices.append(v)
        else:
            self.vertices.insert(index, v)
        meshVertex.addReference(self)

        if calculate:
            self.calculateTextureVertices()
        
        return self

    def removeVertex(self, meshFaceVertex):
        if meshFaceVertex in self.vertices:
            self.vertices.remove(meshFaceVertex)
        meshFaceVertex.vertex.removeReference(self)

    def replaceVertex(self, old, new):
        index = self.vertices.index(old)
        self.vertices[index] = new
        old.vertex.removeReference(self)
        new.vertex.addReference(self)
        self.calculateTextureVertices()

    # the index of the specified MeshVertex (not a MeshFaceVertex)
    # -1 if not found
    def indexOf(self, meshVertex):
        i = 0
        for v in self.vertices:
            if v.vertex == meshVertex:
                return i
            i += 1
        return -1

    def setVertex(self, meshFaceVertex, meshVertex):
        v = MeshFaceVertex(vertex = meshVertex,
                           textureVertex = meshFaceVertex.textureVertex)
        self.replaceVertex(meshFaceVertex, v)
        self.calculateTextureVertices()

    def clearVertices(self):
        for v in self.vertices:
            v.vertex.removeReference(self)
        self.vertices = [ ]
    
    def setTextureTransform(self, shift, rotate, scale):
        self.textureShift = shift
        self.textureRotate = rotate
        self.textureScale = scale
        self.calculateTextureVertices()

    def calculateTextureVertices(self):
        normal = self.getNormal()
        if normal == None:
            return
        normalRot = normal.rotation()

        i = 0
        for oldVertex in self.vertices:
            pos = oldVertex.vertex.getPosition()
            textureVertex = pos.rotate(-normalRot)
            newVertex = MeshFaceVertex(vertex = oldVertex.vertex,
                                       textureVertex = textureVertex)
            self.vertices[i] = newVertex

            i += 1

    # MaterialReference
    def getMaterial(self):
        return self.material

    # doesn't change references
    def setMaterial(self, material):
        self.material = material

    def getNormal(self):
        if len(self.vertices) >= 3:
            return Vector.normal(self.vertices[0].vertex.getPosition(),
                                 self.vertices[1].vertex.getPosition(),
                                 self.vertices[2].vertex.getPosition())
        else:
            return None


class Mesh:
    
    def __init__(self):
        self.vertices = [ ] # list of MeshVertex's
        self.faces = [ ] # list of MeshFace's

    def clone(self):
        newMesh = Mesh()

        newVertices = [v.clone() for v in self.vertices]
        for v in newVertices:
            newMesh.addVertex(v)
        
        for face in self.faces:
            newFace = MeshFace()
            
            for vertex in face.getVertices():
                vertexIndex = self.vertices.index(vertex.vertex)
                newFace.addVertex(newVertices[vertexIndex],
                                  vertex.textureVertex)

            newMesh.addFace(newFace)

        return newMesh

    def getVertices(self):
        return self.vertices

    # clears all vertex references. Do this before adding the vertex to a face
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
            v.vertex.addReference(face)
        return face

    # removing the face deletes all of its vertices
    # it is useless after that.
    def removeFace(self, face):
        self.faces.remove(face)
        face.clearVertices()
