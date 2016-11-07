__author__ = "jacobvanthoog"

from threelib.vectorMath import Vector
from threelib.vectorMath import Rotate

from threelib.edit.base import WorldObject
from threelib.world import World

class EditorState:

    CURRENT_MAJOR_VERSION = 1
    CURRENT_MINOR_VERSION = 0

    SELECT_OBJECTS = 0
    SELECT_FACES = 1
    SELECT_VERTICES = 2

    def __init__(self):
        self.MAJOR_VERSION = EditorState.CURRENT_MAJOR_VERSION
        self.MINOR_VERSION = EditorState.CURRENT_MINOR_VERSION

        self.world = World()

        self.cameraPosition = Vector(-32, 0, 0)
        self.cameraRotation = Rotate(0, 0, 0)
        self.objects = [ ]
        self.worldObject = WorldObject()

        self.selectMode = EditorState.SELECT_OBJECTS
        self.selectedObjects = [ ]
        self.selectedFaces = [ ]
        self.selectedVertices = [ ]

        # initial position for a newly created object
        self.createPosition = Vector(0, 0, 0)

        # adjustor state
        self.relativeCoordinatesEnabled = True
        self.snapEnabled = True
        self.axisLockEnabled = False
        self.translateGridSize = 16.0
        self.rotateGridSize = 15.0 # in degrees
        self.scaleGridSize = 0.25

        self.currentMaterial = None # a material reference

    def onLoad(self):
        self.world.onLoad()

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

    def setCurrentMaterial(self, materialReference):
        if self.currentMaterial != None:
            self.world.removeMaterialReference(self.currentMaterial)

        self.currentMaterial = materialReference

        if self.currentMaterial != None:
            self.currentMaterial.addReference()


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

    # called when adjust is competed successfully
    def complete(self):
        pass

    # called when adjust is cancelled
    def cancel(self):
        pass

    # return a string description of what the adjustor is doing
    def getDescription(self):
        return "Adjust"


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

