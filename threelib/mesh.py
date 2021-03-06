__author__ = "jacobvanthoog"

import math
from threelib.vectorMath import Vector, isclose
from collections import namedtuple
from threelib import vectorMath

# vertex is a MeshVertex
# textureVertex is a Vector
MeshFaceVertex = namedtuple("MeshFaceVertex", ["vertex", "textureVertex"])


class MeshVertex:
    """
    A vertex of a mesh, with a position. The same vertex can be used on multiple
    faces. MeshVertex keeps track of the faces that use it.
    """
    def __init__(self, position):
        self.v = position
        self.references = [ ] # list of MeshFaces that reference this vertex

    def __repr__(self):
        return "MeshVertex @ " + str(self.v)

    def clone(self):
        """
        Return a new mesh vertex at the same position (with no faces using it).
        """
        return MeshVertex(self.v)

    def getPosition(self):
        """
        Get the position of the vertex, as a Vector.
        """
        return self.v

    def setPosition(self, position):
        """
        Set the position of the vertex, and recalculate texture vertices for
        all faces that use this vertex.
        """
        self.v = position
        for face in self.references:
            face.calculateTextureVertices()
            face.verticesChanged()

    def addReference(self, face):
        """
        Add a face that uses this vertex. This should not be called directly
        outside of internal mesh code! It is automatically called as vertices
        are added to faces.
        """
        if face not in self.references:
            self.references.append(face)

    def removeReference(self, face):
        """
        Remove a face that uses this vertex. This should not be called directly
        outside of internal mesh code! It is automatically called as vertices
        are removed from faces.
        """
        if face in self.references:
            self.references.remove(face)

    def clearReferences(self):
        """
        Clear the list of faces that use this vertex. This should not be
        called directly outside of internal mesh code!
        """
        self.references = [ ]

    def numReferences(self):
        """
        Get the number of faces that use this vertex.
        """
        return len(self.references)

    def getReferences(self):
        """
        Get a list of MeshFaces that use this vertex.
        """
        return self.references



class MeshFace:
    """
    A face of a mesh. MeshFaces have vertices that define the face, represented
    by MeshFaceVertex's. These contain both the MeshVertex and the 2d texture
    coordinate as a Vector.
    """
    def __init__(self):
        # a list of MeshFaceVertex's
        self.vertices = [ ]
        self.material = None
        self.textureShift = Vector(0, 0)
        self.textureScale = Vector(32, 32)
        self.textureRotate = 0
        
        self.normal = None
        self.normalUpdated = False

    def __repr__(self):
        return "Face with " + str(self.vertices)
    
    def verticesChanged(self):
        """
        Called when the number or position of vertices on the face has changed.
        """
        # this should never call calculateTextureVertices
        # unless something changes with addVertex
        self.normalUpdated = False

    def getVertices(self):
        """
        Get a list of MeshFaceVertex's representing the face's vertices. The
        vertices are in counterclockwise order.
        """
        return self.vertices

    def addVertex(self, meshVertex, textureVertex=None, index=None):
        """
        Add a MeshVertex to the face. If ``index`` is specified, the vertex will
        be added at the specified index in the list of vertices - otherwise
        it will be added onto the end. If ``textureVertex`` is not specified,
        the texture vertices for each vertex will be recalculated.

        This MeshFace is returned, for easy chaining of ``addVertex`` commands.
        """
        calculate = False
        if textureVertex is None:
            textureVertex = Vector(0,0)
            calculate = True

        v = MeshFaceVertex(vertex=meshVertex, textureVertex=textureVertex)
        if index is None:
            self.vertices.append(v)
        else:
            self.vertices.insert(index, v)
        meshVertex.addReference(self)

        if calculate:
            self.calculateTextureVertices()
        self.verticesChanged()

        return self

    def findFaceVertex(self, meshVertex):
        """
        Given a MeshVertex, find the MeshFaceVertex with that vertex for this
        face. Return None if not found.
        """
        for v in self.vertices:
            if v.vertex == meshVertex:
                return v
        return None

    def removeVertex(self, meshFaceVertex):
        """
        Remove the specified MeshFaceVertex from the face.
        """
        if meshFaceVertex in self.vertices:
            self.vertices.remove(meshFaceVertex)
        meshFaceVertex.vertex.removeReference(self)
        self.verticesChanged()

    def replaceVertex(self, old, new):
        """
        Replace the specified MeshFaceVertex with a new MeshFaceVertex.
        """
        index = self.vertices.index(old)
        self.vertices[index] = new
        old.vertex.removeReference(self)
        new.vertex.addReference(self)
        self.calculateTextureVertices()
        self.verticesChanged()

    def indexOf(self, meshVertex):
        """
        Find the index of the MeshFaceVertex that contains the specified
        MeshVertex. Return -1 if not found.
        """
        i = 0
        for v in self.vertices:
            if v.vertex == meshVertex:
                return i
            i += 1
        return -1

    def setVertex(self, meshFaceVertex, meshVertex):
        """
        Replace the specified MeshFaceVertex with a new MeshVertex.
        """
        v = MeshFaceVertex(vertex = meshVertex,
                           textureVertex = meshFaceVertex.textureVertex)
        self.replaceVertex(meshFaceVertex, v)
        self.calculateTextureVertices()
        self.verticesChanged()

    def clearVertices(self):
        """
        Remove all vertices from the face.
        """
        for v in self.vertices:
            v.vertex.removeReference(self)
        self.vertices = [ ]
        self.verticesChanged()

    def setTextureTransform(self, shift, rotate, scale):
        """
        Set the texture transformation of the face, used for auto-generated
        texture vertices.
        """
        self.textureShift = shift
        self.textureRotate = rotate
        self.textureScale = scale
        self.calculateTextureVertices()

    def copyMaterialInfo(self, face):
        """
        Copy material, texture transform from another face
        """
        self.setMaterial(face.getMaterial())
        self.setTextureTransform(face.textureShift, face.textureRotate,
                                 face.textureScale)

    def calculateTextureVertices(self):
        """
        Recalculate the texture coordinates for each vertex, using the texture
        transformation of the face.
        """
        normal = self.getNormal()
        if normal is None:
            return
        # fix for unpredictable texture vertices with up or down normals
        if isclose(normal.x, 0.0):
            normal = normal.setX(0)
        if isclose(normal.y, 0.0):
            normal = normal.setY(0)
        if isclose(normal.z, 1.0):
            normal = normal.setZ(1)
        if isclose(normal.z, -1.0):
            normal = normal.setZ(-1)

        normalRot = normal.rotation()

        i = 0
        for oldVertex in self.vertices:
            pos = oldVertex.vertex.getPosition()
            textureVertex = pos.inverseRotate(-normalRot)
            textureVertex = Vector(textureVertex.y, -textureVertex.z)

            textureVertex = textureVertex.rotate2(self.textureRotate)
            textureVertex += self.textureShift
            textureVertex /= self.textureScale.setZ(1) # prevent divide z by 0
            # scale for correct aspect ratio of texture
            if self.material is not None:
                if self.material.isLoaded():
                    aspect = self.material.getAspectRatio()
                    if aspect > 1:
                        textureVertex *= Vector(1, aspect, 1)
                    elif aspect < 1:
                        textureVertex *= Vector(1.0 / aspect, 1, 1)

            newVertex = MeshFaceVertex(vertex = oldVertex.vertex,
                                       textureVertex = textureVertex)
            self.vertices[i] = newVertex

            i += 1

    def getMaterial(self):
        """
        Get the face's material. Return a MaterialReference.
        """
        return self.material

    def setMaterial(self, material):
        """
        Set the MaterialReference for this face. The materials' reference counts
        will be updated.
        """
        if self.material is not None:
            self.material.removeReference()
        self.material = material
        if self.material is not None:
            self.material.addReference()
        self.calculateTextureVertices()

    def getNormal(self):
        """
        Get the normal Vector of the face, based on the first 3 vertices.
        Return None if there aren't enough vertices to calculate a normal.
        Each time the vertices of the face change, the normal only has to be
        calculated once - after that it is stored and reused when this method
        is called.
        """
        if not self.normalUpdated:
            if len(self.vertices) >= 3:
                self.normal = Vector.normal(
                    self.vertices[0].vertex.getPosition(),
                    self.vertices[1].vertex.getPosition(),
                    self.vertices[2].vertex.getPosition())
            else:
                self.normal = None
            self.normalUpdated = True
        return self.normal

    def getArea(self):
        """
        Calculate the area of the face.
        """
        if len(self.vertices) < 3:
            return None
        area = 0
        v1 = self.vertices[0].vertex.getPosition()
        for i in range(1, len(self.vertices) - 1):
            v2 = self.vertices[i].vertex.getPosition()
            v3 = self.vertices[i + 1].vertex.getPosition()
            dist1 = v2.distanceTo(v3)
            dist2 = v1.distanceTo(v3)
            dist3 = v1.distanceTo(v2)
            # Heron's formula!
            s = (dist1 + dist2 + dist3) / 2
            area += math.sqrt(s * (s-dist1) * (s-dist2) * (s-dist3))
        return area

    def getPlane(self):
        """
        Get the constants for the plane equation of the face
        (ax + by + cz + d = 0). Return a tuple of (a, b, c, d).
        """
        if len(self.vertices) >= 3:
            return vectorMath.calculatePlaneConstants(
                self.vertices[0].vertex.getPosition(),
                self.getNormal())
        else:
            return None

    def reverse(self):
        """
        Reverse the order of the vertices on this face.
        """
        self.vertices.reverse()

    def getCentroid(self):
        """
        Calculate the centroid of the face polygon.
        """

        normal = self.getNormal()
        normalRot = normal.rotation()

        # http://stackoverflow.com/a/2792459
        centroid = Vector(0, 0)
        signedArea = 0.0

        i = 0
        for i in range(0, len(self.vertices)):
            v0 = self.vertices[i - 1].vertex.getPosition() \
                .inverseRotate(-normalRot)
            v1 = self.vertices[i].vertex.getPosition() \
                .inverseRotate(-normalRot)
            x0 = v0.y
            y0 = v0.z
            x1 = v1.y
            y1 = v1.z
            a = x0 * y1 - x1 * y0
            signedArea += a
            centroid += Vector((x0 + x1) * a, 0)
            centroid += Vector(0, (y0 + y1) * a)

        signedArea *= 0.5
        centroid /= 6.0 * signedArea

        # move centroid back into position
        centroid += Vector(
            self.vertices[0].vertex.getPosition().inverseRotate(-normalRot).x,0)
        centroid = centroid.rotate(normalRot)

        return centroid


class Mesh:

    def __init__(self):
        self.vertices = [ ] # list of MeshVertex's
        self.faces = [ ] # list of MeshFace's

    def clone(self):
        """
        Create a new mesh with identical (but different) vertices and faces.
        """
        newMesh = Mesh()
        newMesh.cloneData(self)
        return newMesh

    def cloneData(self, other):
        """
        Replace all vertices and faces from this mesh with a copy of another
        mesh's
        """
        self.vertices = [v.clone() for v in other.vertices]
        self.faces = [ ]

        for face in other.faces:
            newFace = MeshFace()

            for vertex in face.getVertices():
                vertexIndex = other.vertices.index(vertex.vertex)
                newFace.addVertex(self.vertices[vertexIndex],
                                  vertex.textureVertex)
            newFace.copyMaterialInfo(face)
            self.addFace(newFace)

    def getVertices(self):
        """
        Get a list of MeshVertex's for this mesh.
        """
        return self.vertices

    def addVertex(self, vertex=None):
        """
        Add a MeshVertex to the mesh. If a vertex is not given, a new one is
        created. This clears all of the vertex's references, so do this BEFORE
        adding the vertex to a face. Returns the vertex.
        """
        if vertex is None:
            # can't be used as default value
            # the same vertex object would be used each time
            vertex = MeshVertex(Vector(0,0,0))
        vertex.clearReferences()
        self.vertices.append(vertex)
        return vertex

    def removeVertex(self, vertex, removeFaces=True):
        """
        Remove the vertex from the mesh. If ``removeFaces`` is True, all faces
        that this vertex references will also be removed. Setting this to False
        could be dangerous!
        """
        if removeFaces:
            faces = [ ]
            for face in vertex.getReferences():
                faces.append(face)
            for face in faces:
                self.removeFace(face)
        if vertex in self.vertices:
            self.vertices.remove(vertex)

    def getFaces(self):
        """
        Get a list of MeshFaces for this mesh.
        """
        return self.faces

    def addFace(self, face=None):
        """
        Add a new face to the mesh and return it. If ``face`` is not specified,
        an empty one will be created.
        """
        if face is None:
            # can't be used as default value
            # the same face object would be used each tiem
            face = MeshFace()
        self.faces.append(face)
        for v in face.getVertices():
            v.vertex.addReference(face)
        return face

    def removeFace(self, face):
        """
        Remove a face from the mesh. Removing the face deletes all of its vertices
        It is useless after that.
        """
        self.faces.remove(face)
        face.clearVertices()
        face.setMaterial(None)

    def removeMaterials(self):
        """
        Clear all materials for all faces.
        """
        for face in self.faces:
            face.setMaterial(None)

    def cleanUp(self):
        """
        Combine duplicate vertices and remove unused vertices. See
        ``combineDuplicateVertices`` and ``removeUnusedVertices``.
        """
        self.combineDuplicateVertices()
        self.removeUnusedVertices()

    def removeUnusedVertices(self):
        """
        Remove all vertices that are not used by a face.
        """
        verticesToRemove = [ ]
        for v in self.vertices:
            if v.numReferences() == 0:
                verticesToRemove.append(v)
        for v in verticesToRemove:
            self.vertices.remove(v)

    def combineDuplicateVertices(self):
        """
        Combine multiple vertices at the same position. Fix any face references
        so they point to the same vertex. Also, for individual faces remove
        any duplicate vertices in a row.
        """
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
        verticesToDelete = [ ]
        while i < len(self.vertices):
            v1 = self.vertices[i]
            if v1 in verticesToDelete:
                i += 1
                continue
            for j in range(i + 1, len(self.vertices)):
                v2 = self.vertices[j]
                if v2 in verticesToDelete:
                    continue
                if v1.getPosition().isClose(v2.getPosition()):
                    # replace all instances of v2 in every face with v1
                    for face in list(v2.getReferences()):
                        for vertex in list(face.getVertices()):
                            if vertex.vertex == v2:
                                face.replaceVertex(vertex, MeshFaceVertex(
                                    vertex=v1, textureVertex=Vector(0,0)))
                    verticesToDelete.append(v2)
            i += 1

        for v in verticesToDelete:
            self.vertices.remove(v)

    def addMissingVertices(self):
        for f in self.faces:
            for vertex in f.getVertices():
                v = vertex.vertex
                if v not in self.vertices:
                    self.vertices.append(v)
                    v.addReference(f)

    def isEmpty(self):
        """
        Return true if the mesh has 0 vertices.
        """
        return len(self.vertices) == 0

