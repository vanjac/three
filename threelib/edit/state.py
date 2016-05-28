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
        child.removeFromParent()
        child.setParent(self)
        self.children.append(child)

    def removeChild(self, child):
        child.setParent(None)
        self.children.remove(child)

    def removeFromParent(self):
        if self.parent != None:
            self.parent().removeChild(self)
            

class EditorState:

    SELECT_OBJECTS = 0
    SELECT_FACES = 1
    SELECT_VERTICES = 2

    def __init__(self):
        self.cameraPosition = Vector(0, 0, 0)
        self.cameraRotation = Rotate(0, 0, 0)
        self.objects = [ ]
        
        self.selectMode = EditorState.SELECT_OBJECTS
        self.selectedObjects = [ ]
        self.selectedFaces = [ ]
        self.selectedVertices = [ ]

        # adjustor state
        self.adjustorOriginalValue = (0.0, 0.0, 0.0)
        self.relativeCoordinatesEnabled = True
        self.snapEnabled = True
        self.axisLockEnabled = False
        self.translateGridSize = 16
        self.rotateGridSize = 15 # in degrees
        self.scaleGridSize = 0.1

# used for adjusting an objects position, rotation, etc using the mouse
# an abstract class
class Adjustor:
    
    # should return a tuple of 3 Vectors -- the current values of the axes
    # these are absolute values
    def getAxes(self):
        pass

    # set the values of the axes, with a tuple
    def setAxes(self, values):
        pass


class TranslateAdjustor:

    def __init__(self, editorObject):
        self.editorObject = editorObject

    def getAxes(self):
        return self.editorObject.getPosition().getTuple()

    def setAxes(self, values):
        self.editorObject.setPosition(Vector(values[0], values[1], values[2]))

# rotate adjustor doesn't use absolute rotations provided by the editorObject
# because some objects don't use those
class RotateAdjustor:

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


class FaceSelection:
    
    def __init__(self, editorObject, face):
        self.editorObject = editorObject
        self.face = face

class VertexSelection:
    
    def __init__(self, editorObject, vertex):
        self.editorObject = editorObject
        self.vertex = vertex

