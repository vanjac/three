__author__ = "vantjac"

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


class TranslateAdjustor(Adjustor):

    def __init__(self, editorObject):
        self.editorObject = editorObject

    def getAxes(self):
        return self.editorObject.getPosition().getTuple()

    def setAxes(self, values):
        self.editorObject.setPosition(Vector(values[0], values[1], values[2]))

    def gridType(self):
        return Adjustor.TRANSLATE

# rotate adjustor doesn't use absolute rotation values provided by the
# editorObject because some objects don't use those
class RotateAdjustor(Adjustor):

    def __init__(self, editorObject):
        self.editorObject = editorObject
        self.currentRotation = self.editorObject.getRotation()

    def getAxes(self):
        return self.currentRotation.getTuple()

    def setAxes(self, values):
        nextRotation = Rotate(values[0], values[1], values[2])
        diff = nextRotation - self.currentRotation
        self.editorObject.setRotation(self.editorObject.getRotation() + diff)
        self.currentRotation = nextRotation

    def gridType(self):
        return Adjustor.ROTATE
