__author__ = "vantjac"

import math
from threelib.vectorMath import Vector
from threelib.vectorMath import Rotate
from threelib.edit.state import Adjustor
# used by ExtrudeAdjustor:
from threelib.mesh import *
from threelib.edit.objects import MeshObject


class NoOpAdjustor(Adjustor):
    
    def __init__(self, gridType):
        self.gridType = gridType
        self.value = (0, 0, 0)

    def getAxes(self):
        return self.value

    def setAxes(self, values):
        self.value = values

    def gridType(self):
        return self.gridType


class TestAdjustor(Adjustor):

    def __init__(self, initialValue = (0, 0, 0)):
        self.value = initialValue

    def getAxes(self):
        return self.value

    def setAxes(self, values):
        print("TestAdjustor moved to", values)
        self.value = values

    def gridType(self):
        return Adjustor.TRANSLATE


class TranslateAdjustor(Adjustor):

    def __init__(self, editorObject):
        self.editorObject = editorObject

    def getAxes(self):
        return self.editorObject.getPosition().getTuple()

    def setAxes(self, values):
        self.editorObject.setPosition(Vector.fromTuple(values))

    def gridType(self):
        return Adjustor.TRANSLATE

    def getDescription(self):
        return "Translate object"


class VertexTranslateAdjustor(Adjustor):

    def __init__(self, meshVertex, editorObject):
        self.origin = editorObject.getPosition()
        self.vertex = meshVertex

    def getAxes(self):
        return (self.vertex.getPosition() + self.origin).getTuple()

    def setAxes(self, values):
        self.vertex.setPosition(Vector.fromTuple(values) - self.origin)

    def gridType(self):
        return Adjustor.TRANSLATE

    def getDescription(self):
        return "Translate vertex"


class MultiTranslateAdjustor(Adjustor):

    def __init__(self, adjustors):
        self.adjustors = list(adjustors)

        # calculate the average initial position
        self.average = Vector(0.0, 0.0, 0.0)
        for a in adjustors:
            self.average += Vector.fromTuple(a.getAxes())
        self.average /= float(len(adjustors))

        # calculate each adjustor's offset from the average
        self.offsets = [ ] # array of Vectors for each adjustor
        for a in adjustors:
            offset = Vector.fromTuple(a.getAxes()) - self.average
            self.offsets.append(offset)

    def getAxes(self):
        return self.average.getTuple()

    def setAxes(self, values):
        self.average = Vector.fromTuple(values)
        i = 0
        for a in self.adjustors:
            a.setAxes((self.average + self.offsets[i]).getTuple())
            i += 1

    def gridType(self):
        return Adjustor.TRANSLATE

    def getDescription(self):
        return "Translate " + str(len(self.adjustors)) + " objects"


class OriginAdjustor(Adjustor):

    def __init__(self, editorObject):
        self.editorObject = editorObject

    def getAxes(self):
        return self.editorObject.getPosition().getTuple()

    def setAxes(self, values):
        v = Vector.fromTuple(values)
        diff = v - self.editorObject.getPosition()
        self.editorObject.setPosition(v)

        if self.editorObject.getMesh() != None:
            for vertex in self.editorObject.getMesh().getVertices():
                vertex.setPosition(vertex.getPosition() - diff)

    def gridType(self):
        return Adjustor.TRANSLATE

    def getDescription(self):
        return "Change object origin"


# convert a tuple of 3 values to degrees
def tupleToDegrees(t):
    return (math.degrees(t[0]), math.degrees(t[1]), math.degrees(t[2]))

# convert a tuple of 3 values to radians
def tupleToRadians(t):
    return (math.radians(t[0]), math.radians(t[1]), math.radians(t[2]))


class RotateAdjustor(Adjustor):

    def __init__(self, editorObject):
        self.editorObject = editorObject

    def getAxes(self):
        return tupleToDegrees(self.editorObject.getRotation().getTuple())

    def setAxes(self, values):
        self.editorObject.setRotation(Rotate.fromTuple(tupleToRadians(values)))

    def gridType(self):
        return Adjustor.ROTATE

    def complete(self):
        self.editorObject.applyRotation()

    def getDescription(self):
        return "Rotate object"


class MultiRotateAdjustor(Adjustor):

    def __init__(self, translateAdjustors, rotateAdjustors):
        self.translators = list(translateAdjustors)
        self.rotators = list(rotateAdjustors)

        # calculate the average initial position
        self.average = Vector(0.0, 0.0, 0.0)
        for a in self.translators:
            self.average += Vector.fromTuple(a.getAxes())
        self.average /= float(len(self.translators))

        # calculate each adjustor's offset from the average
        self.offsets = [ ] # array of Vectors for each adjustor
        for a in self.translators:
            offset = Vector.fromTuple(a.getAxes()) - self.average
            self.offsets.append(offset)

        self.currentRotate = Rotate(0, 0, 0)

    def getAxes(self):
        return tupleToDegrees(self.currentRotate.getTuple())

    def setAxes(self, values):
        newRotate = Rotate.fromTuple(tupleToRadians(values))
        diff = newRotate - self.currentRotate
        self.currentRotate = newRotate
        
        for i in range(0, len(self.translators)):
            offset = self.offsets[i]
            offset = offset.rotate(self.currentRotate)
            self.translators[i].setAxes((offset + self.average).getTuple())
            rotate = Rotate.fromTuple(
                tupleToRadians(self.rotators[i].getAxes()))
            rotate += diff
            self.rotators[i].setAxes(tupleToDegrees(rotate.getTuple()))

    def gridType(self):
        return Adjustor.ROTATE

    def getDescription(self):
        return "Rotate " + str(len(self.rotators)) + " objects"


class ScaleAdjustor(Adjustor):

    # edges is a tuple of 3 values for each axis. the values can be 0, to scale
    # in both directions; 1 to scale only the higher edge; or -1, to scale only
    # the lower edge
    # if resize is true, the adjustor will use a TRANSLATE grid type instead of
    # SCALE, and the values will be the bounds dimensions
    def __init__(self, editorObject, resize=False):
        self.editorObject = editorObject
        
        if resize:
            self.scale = self.editorObject.getDimensions()
        else:
            self.scale = Vector(1.0, 1.0, 1.0)

        self.resize = resize

    def getAxes(self):
        return self.scale.getTuple()

    def setAxes(self, values):
        v = Vector.fromTuple(values)
        if v.x <= 0:
            v = v.setX(self.scale.x)
        if v.y <= 0:
            v = v.setY(self.scale.y)
        if v.z <= 0:
            v = v.setZ(self.scale.z)
        self.editorObject.scale(v / self.scale)
        self.scale = v

    def gridType(self):
        if self.resize:
            return Adjustor.TRANSLATE
        else:
            return Adjustor.SCALE

    def getDescription(self):
        return "Scale object"


class MultiVertexScaleAdjustor(Adjustor):
    
    def __init__(self, vertices, edges, resize=False):
        self.vertices = list(vertices)
        
        average = Vector(0.0, 0.0, 0.0)
        firstVertexPos = self.vertices[0].getPosition()
        lowX = firstVertexPos.x
        lowY = firstVertexPos.y
        lowZ = firstVertexPos.z
        highX = firstVertexPos.x
        highY = firstVertexPos.y
        highZ = firstVertexPos.z
        for v in self.vertices:
            pos = v.getPosition()
            average += pos
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
        average /= len(self.vertices)
        lowBound = Vector(lowX, lowY, lowZ)
        highBound = Vector(highX, highY, highZ)
        dimensions = highBound - lowBound

        if resize:
            self.scale = dimensions
        else:
            self.scale = Vector(1.0, 1.0, 1.0)

        self.edges = Vector.fromTuple(edges)
        self.originPoint = average - (dimensions/2 * self.edges)

        self.resize = resize

    def getAxes(self):
        return self.scale.getTuple()

    def setAxes(self, values):
        v = Vector.fromTuple(values)
        if v.x <= 0:
            v = v.setX(self.scale.x)
        if v.y <= 0:
            v = v.setY(self.scale.y)
        if v.z <= 0:
            v = v.setZ(self.scale.z)
        for vertex in self.vertices:
            pos = vertex.getPosition()
            pos = (pos - self.originPoint) * (v / self.scale) + self.originPoint
            vertex.setPosition(pos)
        self.scale = v

    def gridType(self):
        if self.resize:
            return Adjustor.TRANSLATE
        else:
            return Adjustor.SCALE

    def getDescription(self):
        return "Scale " + str(len(self.vertices)) + " vertices"

class MultiScaleAdjustor(Adjustor):
    
    def __init__(self, editorObjects, edges, resize=False):
        self.editorObjects = list(editorObjects)

        firstObjectBounds = editorObjects[0].getBounds()
        firstObjectPos = editorObjects[0].getPosition()
        lowBound = firstObjectBounds[0] + firstObjectPos
        highBound = firstObjectBounds[1] + firstObjectPos

        for o in editorObjects:
            pos = o.getPosition()
            bounds = o.getBounds()
            low = bounds[0] + pos
            high = bounds[1] + pos
            if low.x < lowBound.x:
                lowBound = lowBound.setX(low.x)
            if low.y < lowBound.y:
                lowBound = lowBound.setY(low.y)
            if low.z < lowBound.z:
                lowBound = lowBound.setZ(low.z)
            if high.x > highBound.x:
                highBound = highBound.setX(high.x)
            if high.y > highBound.y:
                highBound = highBound.setY(high.y)
            if high.z > highBound.z:
                highBound = highBound.setZ(high.z)

        center = (lowBound + highBound) / 2
        dimensions = highBound - lowBound

        if resize:
            self.scale = dimensions
        else:
            self.scale = Vector(1.0, 1.0, 1.0)

        self.edges = Vector.fromTuple(edges)
        self.originPoint = center - (dimensions/2 * self.edges)

        self.resize = resize

    def getAxes(self):
        return self.scale.getTuple()

    def setAxes(self, values):
        v = Vector.fromTuple(values)
        if v.x <= 0:
            v = v.setX(self.scale.x)
        if v.y <= 0:
            v = v.setY(self.scale.y)
        if v.z <= 0:
            v = v.setZ(self.scale.z)
        for o in self.editorObjects:
            o.scale(v / self.scale)
            pos = o.getPosition()
            pos = (pos - self.originPoint) * (v / self.scale) + self.originPoint
            o.setPosition(pos)
        self.scale = v

    def gridType(self):
        if self.resize:
            return Adjustor.TRANSLATE
        else:
            return Adjustor.SCALE

    def getDescription(self):
        return "Scale " + str(len(self.editorObjects)) + " objects"


class ExtrudeAdjustor(Adjustor):
    
    # meshObject is the mesh object that the face comes from
    def __init__(self, face, meshObject, state):
        self.extrudeAmount = 0
        self.state = state
        
        newMesh = Mesh()
        self.newEditorObject = meshObject.clone()
        self.newEditorObject.setMesh(newMesh)
        state.objects.append(self.newEditorObject)
        
        baseFace = MeshFace()
        self.extrudedFace = MeshFace()
        
        for vertex in face.getVertices():
            newVertex1 = vertex.vertex.clone()
            newVertex2 = vertex.vertex.clone()
            newMesh.addVertex(newVertex1)
            newMesh.addVertex(newVertex2)
            newTextureVertex = vertex.textureVertex
            
            self.extrudedFace.addVertex(newVertex2, newTextureVertex)
            # add vertices in reverse order
            baseFace.addVertex(newVertex1, newTextureVertex, index=0)
            
        vertices = self.extrudedFace.getVertices()
        self.normal = Vector.normal(vertices[0].vertex.getPosition(),
                                    vertices[1].vertex.getPosition(),
                                    vertices[2].vertex.getPosition())

        newMesh.addFace(baseFace)
        newMesh.addFace(self.extrudedFace)
        baseFace.copyMaterialInfo(face)
        self.extrudedFace.copyMaterialInfo(face)

        numVertices = len(face.getVertices())
        for i in range(0, numVertices):
            j = numVertices - i - 1
            iIncr = (i + 1) % numVertices
            jIncr = (j - 1) % numVertices
            if jIncr < 0:
                jIncr += numVertices

            sideFace = MeshFace()
            v1 = self.extrudedFace.getVertices()[iIncr].vertex
            v2 = self.extrudedFace.getVertices()[i].vertex
            v3 = baseFace.getVertices()[j].vertex
            v4 = baseFace.getVertices()[jIncr].vertex
            sideFace.addVertex(v1).addVertex(v2).addVertex(v3).addVertex(v4)
                
            newMesh.addFace(sideFace)
            sideFace.copyMaterialInfo(face)
                
            
    def getAxes(self):
        return (self.extrudeAmount, 0.0, 0.0)

    def setAxes(self, values):
        diff = values[0] - self.extrudeAmount
        self.extrudeAmount = values[0]
        
        for vertex in self.extrudedFace.getVertices():
            vertex.vertex.setPosition(vertex.vertex.getPosition()
                                      + (self.normal * diff))
            

    def cancel(self):
        self.state.objects.remove(self.newEditorObject)

    def complete(self):
        # TODO: center origin of new object?
        pass

    def gridType(self):
        return Adjustor.TRANSLATE

    def getDescription(self):
        return "Extrude face"


class MultiExtrudeAdjustor(Adjustor):

    def __init__(self, adjustors):
        self.adjustors = adjustors
        self.extrudeAmount = 0

    def getAxes(self):
        return (self.extrudeAmount, 0.0, 0.0)

    def setAxes(self, values):
        self.extrudeAmount = values[0]
        values = self.getAxes()
        for adjustor in self.adjustors:
            adjustor.setAxes(values)

    def cancel(self):
        for adjustor in self.adjustors:
            adjustor.cancel()

    def complete(self):
        for adjustor in self.adjustors:
            adjustor.complete()

    def gridType(self):
        return Adjustor.TRANSLATE

    def getDescription(self):
        return "Extrude faces"


class ArrowStartAdjustor(Adjustor):

    def __init__(self, editorActions):
        self.editorActions = editorActions

    def getAxes(self):
        return self.editorActions.arrowStart.getTuple()

    def setAxes(self, values):
        self.editorActions.arrowStart = Vector.fromTuple(values)
        self.editorActions.arrowEnd = self.editorActions.arrowStart

    def cancel(self):
        self.editorActions.arrowShown = False

    def gridType(self):
        return Adjustor.TRANSLATE

    def getDescription(self):
        return "Arrow start"

class ArrowEndAdjustor(Adjustor):

    def __init__(self, editorActions):
        self.editorActions = editorActions

    def getAxes(self):
        return self.editorActions.arrowEnd.getTuple()

    def setAxes(self, values):
        self.editorActions.arrowEnd = Vector.fromTuple(values)

    def cancel(self):
        self.editorActions.arrowShown = False

    def gridType(self):
        return Adjustor.TRANSLATE

    def getDescription(self):
        return "Arrow end"
