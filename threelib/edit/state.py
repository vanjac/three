__author__ = "vantjac"

from threelib.vectorMath import Vector
from threelib.vectorMath import Rotate

# abstract class
class EditorObject:

    # return a string
    def getName(self):
        pass

    # string describing the EditorObject
    def getType(self):
        pass

    # return a Vector
    def getPosition(self):
        pass

    # return a Rotation
    def getRotation(self):
        pass

    # return a tuple of 2 vectors (minCoords, maxCoords)
    def getBounds(self):
        pass

    def setPosition(self, position):
        pass

    def setRotation(self, rotation):
        pass

    def setScale(self, scale):
        pass

    def getMesh(self):
        pass

    # use OpenGL to draw the object. Draw it at the origin with no rotation (but
    # with scaling) -- it is the editor's responsibility to position and rotate
    # it.
    def drawObject(self):
        pass

    # color is a tuple of (r, g, b). Draw with OpenGL.
    def drawSelectHull(self, color):
        pass

    # a dictionary mapping strings to strings
    def getProperties(self):
        pass

    def setProperties(self):
        pass

    # return another EditorObject
    def getParent(self):
        pass

    # return a list of EditorObjects
    def getChildren(self):
        pass


class EditorState:
    
    def __init__(self):
        self.cameraPosition = Vector(0, 0, 0)
        self.cameraRotation = Rotate(0, 0, 0)
