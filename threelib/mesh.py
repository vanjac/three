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

    def __repr__(self):
        return "MeshVertex @ " + str(self.v)

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
        self.textureScale = Vector(32, 32)
        self.textureRotate = 0

    def __repr__(self):
        return "Face with " + str(self.vertices)

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

    def findFaceVertex(self, meshVertex):
        for v in self.vertices:
            if v.vertex == meshVertex:
                return v
        return None

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
            textureVertex = Vector(textureVertex.y, textureVertex.z)

            textureVertex = textureVertex.rotate2(self.textureRotate)
            textureVertex += self.textureShift
            textureVertex /= self.textureScale.setZ(1) # prevent divide z by 0

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

    def reverse(self):
        print("reverse!")
        self.vertices.reverse()


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
    def addVertex(self, vertex=None):
        if vertex == None:
            # can't be used as default value
            # the same vertex object would be used each time
            vertex = MeshVertex(Vector(0,0,0))
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
        if vertex in self.vertices:
            self.vertices.remove(vertex)

    def getFaces(self):
        return self.faces

    def addFace(self, face=None):
        if face == None:
            # can't be used as default value
            # the same face object would be used each tiem
            face = MeshFace()
        self.faces.append(face)
        for v in face.getVertices():
            v.vertex.addReference(face)
        return face

    # removing the face deletes all of its vertices
    # it is useless after that.
    def removeFace(self, face):
        self.faces.remove(face)
        face.clearVertices()

    def cleanUp(self):
        self.combineDuplicateVertices()
        self.removeUnusedVertices()

    def removeUnusedVertices(self):
        verticesToRemove = [ ]
        for v in self.vertices:
            if v.numReferences() == 0:
                verticesToRemove.append(v)
        for v in verticesToRemove:
            self.vertices.remove(v)

    def combineDuplicateVertices(self):
        # remove duplicate vertices in a row for individual faces
        for face in self.getFaces():
            verticesToRemove = [ ]
            i = 0
            for vertex in face.getVertices():
                if vertex.vertex.getPosition().isClose(
                        face.getVertices()[i - 1].vertex.getPosition()):
                    verticesToRemove.append(vertex)
                i += 1
            for v in verticesToRemove:
                face.removeVertex(v)

        i = 0
        while i < len(self.vertices):
            v1 = self.vertices[i]
            verticesToDelete = [ ]
            for j in range(i + 1, len(self.vertices)):
                v2 = self.vertices[j]
                if v1.getPosition().isClose(v2.getPosition()):
                    # replace all instances of v2 in every face with v1
                    for face in v2.getReferences():
                        for vertex in face.getVertices():
                            if vertex.vertex == v2:
                                face.replaceVertex(vertex, MeshFaceVertex(
                                    vertex=v1, textureVertex=Vector(0,0)))
                    verticesToDelete.append(v2)
            for v in verticesToDelete:
                self.vertices.remove(v)

            i += 1
