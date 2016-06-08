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

class VertexTranslateAdjustor(Adjustor):

    def __init__(self, meshVertex):
        self.vertex = meshVertex

    def getAxes(self):
        return self.vertex.getPosition().getTuple()

    def setAxes(self, values):
        self.vertex.setPosition(Vector.fromTuple(values))

    def gridType(self):
        return Adjustor.TRANSLATE

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

# rotate adjustor doesn't use absolute rotation values provided by the
# editorObject because some objects don't use those
class RotateAdjustor(Adjustor):

    def __init__(self, editorObject):
        self.editorObject = editorObject
        self.currentRotation = self.editorObject.getRotation()

    def getAxes(self):
        t = self.currentRotation.getTuple()
        return (math.degrees(t[0]), math.degrees(t[1]), math.degrees(t[2]))

    def setAxes(self, values):
        nextRotation = Rotate.fromTuple((
            math.radians(values[0]),
            math.radians(values[1]),
            math.radians(values[2])))
        diff = nextRotation - self.currentRotation
        self.editorObject.setRotation(self.editorObject.getRotation() + diff)
        self.currentRotation = nextRotation

    def gridType(self):
        return Adjustor.ROTATE

