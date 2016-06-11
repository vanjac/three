__author__ = "vantjac"

from threelib.vectorMath import Vector
from threelib.vectorMath import Rotate

# abstract class
class EditorObject:
    
    def __init__(self):
        self.name = ""
        self.children = [ ]
        self.parent = None
        self.selected = False

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

    # factor is a vector
    def scale(self, factor):
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
    
    def isSelected(self):
        return self.selected

    def setSelected(self, selected):
        self.selected = selected


class EditorState:

    SELECT_OBJECTS = 0
    SELECT_FACES = 1
    SELECT_VERTICES = 2

    def __init__(self):
        self.cameraPosition = Vector(-32, 0, 0)
        self.cameraRotation = Rotate(0, 0, 0)
        self.objects = [ ]
        
        self.selectMode = EditorState.SELECT_OBJECTS
        self.selectedObjects = [ ]
        self.selectedFaces = [ ]
        self.selectedVertices = [ ]

        # adjustor state
        self.relativeCoordinatesEnabled = True
        self.snapEnabled = True
        self.axisLockEnabled = False
        self.translateGridSize = 16
        self.rotateGridSize = 15 # in degrees
        self.scaleGridSize = 0.1

    # only required for objects -- faces and vertices just have to be added to
    # the list
    def select(self, editorObject):
        if editorObject not in self.selectedObjects:
            self.selectedObjects.append(editorObject)
        editorObject.setSelected(True)

    def deselect(self, editorObject):
        if editorObject in self.selectedObjects:
            self.selectedObjects.remove(editorObject)
        editorObject.setSelected(False)

    # for object select mode only

    def selectAll(self):
        for o in self.objects:
            o.setSelected(True)
        self.selectedObjects = list(self.objects)
        
    def deselectAll(self):
        for o in self.selectedObjects:
            o.setSelected(False)
        self.selectedObjects = [ ]
    
    def getGridSize(self, gridType):
        if gridType == Adjustor.TRANSLATE:
            return self.translateGridSize
        if gridType == Adjustor.ROTATE:
            return self.rotateGridSize
        if gridType == Adjustor.SCALE:
            return self.scaleGridSize
        return None

    def setGridSize(self, gridType, value):
        if gridType == Adjustor.TRANSLATE:
            self.translateGridSize = value
        if gridType == Adjustor.ROTATE:
            self.rotateGridSize = value
        if gridType == Adjustor.SCALE:
            self.scaleGridSize = value


# used for adjusting an objects position, rotation, etc using the mouse
# an abstract class
class Adjustor:
    
    TRANSLATE = 0
    ROTATE = 1
    SCALE = 2
    
    # should return a tuple of 3 Vectors -- the current values of the axes
    # these are absolute values
    def getAxes(self):
        pass

    # set the values of the axes, with a tuple
    def setAxes(self, values):
        pass

    # return the type of grid the adjustor snaps to
    # one of the constants above
    def gridType(self):
        pass


class FaceSelection:
    # face is a MeshFace
    def __init__(self, editorObject, face):
        self.editorObject = editorObject
        self.face = face

class VertexSelection:
    # vertex is a MeshVertex
    def __init__(self, editorObject, vertex):
        self.editorObject = editorObject
        self.vertex = vertex

