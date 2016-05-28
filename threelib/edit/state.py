__author__ = "vantjac"

from threelib.vectorMath import Vector
from threelib.vectorMath import Rotate

# abstract class
class EditorObject:
    
    def __init__(self):
        self.name = ""
        self.children = [ ]
        self.parent = None

    # return a string
    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name

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
        return self.parent

    # should only be called by other EditorObjects
    def setParent(self, parent):
        self.parent = parent

    # return a list of EditorObjects
    def getChildren(self):
        return self.children

    def addChild(self, child):
        if child.getParent() != None:
            child.getParent().removeChild(child)
        child.setParent(self)
        self.children.append(child)

    def removeChild(self, child):
        child.setParent(None)
        self.children.remove(child)
            

class EditorState:
    
    def __init__(self):
        self.cameraPosition = Vector(0, 0, 0)
        self.cameraRotation = Rotate(0, 0, 0)
        self.objects = [ ]


# used for adjusting an objects position, rotation, etc using the mouse
# an abstract class
class Adjustor:
    
    # should return a tuple of 3 Vectors -- the current values of the axes
    def getAxes(self):
        pass

    # set the values of the axes, with a tuple
    def setAxes(self, values):
        pass
