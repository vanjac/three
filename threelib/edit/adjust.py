__author__ = "vantjac"

import math
from threelib.vectorMath import Vector
from threelib.vectorMath import Rotate
from threelib.edit.state import Adjustor


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
    def __init__(self, editorObject, edges, resize=False):
        self.editorObject = editorObject
        
        if resize:
            self.scale = self.editorObject.getDimensions()
        else:
            self.scale = Vector(1.0, 1.0, 1.0)

        self.edges = Vector.fromTuple(edges)
        self.originPoint = self.editorObject.getCenter() \
                           - (self.editorObject.getDimensions()/2 * self.edges)

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
        self.editorObject.setPosition(self.originPoint
            + (self.editorObject.getDimensions()/2 * self.edges))
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
