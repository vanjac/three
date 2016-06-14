__author__ = "vantjac"

from threelib.edit.state import *
from threelib.vectorMath import Vector
from threelib.vectorMath import Rotate
from threelib.edit.objects import *
from threelib.edit.adjust import *

from threelib import files

class EditorActions:

    X = 0
    Y = 1
    Z = 2

    ROTATE_GRID_SIZES = [5.0, 10.0, 15.0, 20.0, 30.0, 40.0, 45.0]

    def __init__(self, editorMain, state=None):
        if state == None:
            self.state = EditorState()
        else:
            self.state = state
        self.editorMain = editorMain
        self.currentCommand = ""
        self.movingCamera = False
        self.lookSpeed = .005
        self.flySpeed = 2.0
        self.fly = Vector(0, 0, 0) # each component can be 0, 1, or -1

        # adjust mode
        self.inAdjustMode = False
        self.adjustor = None
        self.adjustorOriginalValue = (0.0, 0.0, 0.0)
        self.selectedAxes = (EditorActions.X, EditorActions.Y)
        self.adjustMouseMovement = (0, 0) # in snap mode
        self.adjustMouseGrid = 16 # number of pixels per grid line

        # flags
        self.selectAtCursorOnDraw = False
        self.selectMultiple = False
    
    
    def saveFile(self):
        print("Saving map... ", end="")
        files.saveMapState(files.getCurrentMap(), self.state)
        print("Done")

    def deleteSelected(self):
        if self.state.selectMode == EditorState.SELECT_FACES:
            print("Faces cannot be deleted")
        elif self.state.selectMode == EditorState.SELECT_VERTICES:
            print("Vertices cannot be deleted")
        elif len(self.state.selectedObjects) == 0:
            print("Nothing selected")
        else:
            print("Delete selected objects")
            for o in self.state.selectedObjects:
                o.removeFromParent()
                self.state.objects.remove(o)
            self.state.deselectAll()

    def selectMode(self, mode):
        self.state.selectMode = mode
        self.state.deselectAll()
        self.state.selectedVertices = [ ]
        self.state.selectedFaces = [ ]

    def createBox(self):
        print("Create box")
        self.selectMode(EditorState.SELECT_OBJECTS)
        self.state.deselectAll()
        box = MeshObject(self.state.translateGridSize)
        box.setPosition(Vector(0, 0, 0))
        self.state.objects.append(box)
        self.state.select(box)
        self.setupAdjustMode(TranslateAdjustor(box))

    def selectAll(self):
        if self.state.selectMode == EditorState.SELECT_OBJECTS:
            if len(self.state.selectedObjects) == 0:
                self.state.selectAll()
                print("Select", len(self.state.selectedObjects), "objects")
            else:
                self.state.deselectAll()
                print("Select none")
        elif self.state.selectMode == EditorState.SELECT_FACES:
            if len(self.state.selectedFaces) == 0:
                for o in self.state.objects:
                    if o.getMesh() != None:
                        for f in o.getMesh().getFaces():
                            self.state.selectedFaces.append(
                                FaceSelection(o, f))
                print("Select", len(self.state.selectedFaces), "faces")
            else:
                self.state.selectedFaces = [ ]
                print("Select none")
        elif self.state.selectMode == EditorState.SELECT_VERTICES:
            if len(self.state.selectedVertices) == 0:
                for o in self.state.objects:
                    if o.getMesh() != None:
                        for v in o.getMesh().getVertices():
                            self.state.selectedVertices.append(
                                VertexSelection(o, v))
                print("Select", len(self.state.selectedVertices), "vertices")
            else:
                self.state.selectedVertices = [ ]
                print("Select none")

    def translateSelected(self):
        if self.state.selectMode == EditorState.SELECT_OBJECTS:
            if len(self.state.selectedObjects) == 0:
                print("Nothing selected")
            elif len(self.state.selectedObjects) == 1:
                print("Translate object")
                self.setupAdjustMode(TranslateAdjustor(
                    self.state.selectedObjects[0]))
            else:
                print("Translate objects")
                adjustors = [ ]
                for o in self.state.selectedObjects:
                    adjustors.append(TranslateAdjustor(o))
                self.setupAdjustMode(MultiTranslateAdjustor(adjustors))
        elif self.state.selectMode == EditorState.SELECT_VERTICES:
            if len(self.state.selectedVertices) == 0:
                print("Nothing selected")
            elif len(self.state.selectedVertices) == 1:
                print("Translate vertex")
                selected = self.state.selectedVertices[0]
                self.setupAdjustMode(VertexTranslateAdjustor(
                    selected.vertex,
                    selected.editorObject))
            else:
                print("Translate vertices")
                adjustors = [ ]
                for v in self.state.selectedVertices:
                    adjustors.append(VertexTranslateAdjustor(
                        v.vertex,
                        v.editorObject))
                self.setupAdjustMode(MultiTranslateAdjustor(adjustors))
        elif self.state.selectMode == EditorState.SELECT_FACES:
            if len(self.state.selectedFaces) == 0:
                print("Nothing selected")
            else:
                print("Translate face(s)")
                adjustors = [ ]
                for f in self.state.selectedFaces:
                    for v in f.face.getVertices():
                        adjustors.append(VertexTranslateAdjustor(
                            v.vertex,
                            f.editorObject))
                self.setupAdjustMode(MultiTranslateAdjustor(adjustors))
                 
    def rotateSelected(self):
        if self.state.selectMode == EditorState.SELECT_OBJECTS:
            if len(self.state.selectedObjects) == 0:
                print("Nothing selected")
            elif len(self.state.selectedObjects) == 1:
                print("Rotate object")
                self.setupAdjustMode(RotateAdjustor(
                    self.state.selectedObjects[0]))
            else:
                print("Rotate objects")
                translators = [ ]
                rotators = [ ]
                for o in self.state.selectedObjects:
                    translators.append(TranslateAdjustor(o))
                    rotators.append(RotateAdjustor(o))
                self.setupAdjustMode(MultiRotateAdjustor(translators, rotators))
        elif self.state.selectMode == EditorState.SELECT_VERTICES:
            if len(self.state.selectedVertices) == 0:
                print("Nothing selected")
            elif len(self.state.selectedVertices) == 1:
                print("Single vertex cannot be rotated")
            else:
                print("Rotate vertices")
                translators = [ ]
                rotators = [ ]
                for v in self.state.selectedVertices:
                    translators.append(VertexTranslateAdjustor(
                        v.vertex,
                        v.editorObject))
                    rotators.append(NoOpAdjustor(Adjustor.ROTATE))
                self.setupAdjustMode(MultiRotateAdjustor(translators, rotators))
        elif self.state.selectMode == EditorState.SELECT_FACES:
            if len(self.state.selectedFaces) == 0:
                print("Nothing selected")
            else:
                print("Rotate face(s)")
                translators = [ ]
                rotators = [ ]
                for f in self.state.selectedFaces:
                    for v in f.face.getVertices():
                        translators.append(VertexTranslateAdjustor(
                            v.vertex,
                            f.editorObject))
                        rotators.append(NoOpAdjustor(Adjustor.ROTATE))
                self.setupAdjustMode(MultiRotateAdjustor(translators, rotators))

    # see ScaleAdjustor for description of edges
    def scaleSelected(self, edges):
        if self.state.selectMode == EditorState.SELECT_OBJECTS:
            if len(self.state.selectedObjects) == 0:
                print("Nothing selected")
            elif len(self.state.selectedObjects) == 1:
                print("Scale object with edges", edges)
                self.setupAdjustMode(ScaleAdjustor(
                    self.state.selectedObjects[0], edges))
            else:
                print("Scale objects")
                print("Not supported yet")
        elif self.state.selectMode == EditorState.SELECT_VERTICES:
            if len(self.state.selectedVertices) == 0:
                print("Nothing selected")
            elif len(self.state.selectedVertices) == 1:
                print("Single vertex cannot be scaled")
            else:
                print("Scale vertices with edges", edges)
                print("Not supported yet")
        elif self.state.selectMode == EditorState.SELECT_FACES:
            if len(self.state.selectedFaces) == 0:
                print("Nothing selected")
            else:
                print("Scale face(s) with edges", edges)
                print("Not supported yet")

    def setupAdjustMode(self, adjustor):
        self.inAdjustMode = True
        self.adjustor = adjustor
        self.adjustorOriginalValue = adjustor.getAxes()
        self.adjustMouseMovement = (0, 0)
        self.editorMain.lockMouse()

    def selectAtCursor(self, multiple=False):
        self.selectAtCursorOnDraw = True
        self.selectMultiple = multiple


    # ADJUST MODE ACTIONS:

    def selectAdjustAxis(self, axis):
        self.selectedAxes = (self.selectedAxes[1], axis)

    def increaseGrid(self):
        gridType = self.adjustor.gridType()
        if self.adjustor.gridType() == Adjustor.ROTATE:
            current = self.state.getGridSize(gridType)
            for size in EditorActions.ROTATE_GRID_SIZES:
                if size > current:
                    self.state.setGridSize(gridType, size)
                    break
        else:
            self.multiplyGrid(2)

    def decreaseGrid(self):
        gridType = self.adjustor.gridType()
        if self.adjustor.gridType() == Adjustor.ROTATE:
            current = self.state.getGridSize(gridType)
            previous = EditorActions.ROTATE_GRID_SIZES[0]
            for size in EditorActions.ROTATE_GRID_SIZES:
                if size >= current:
                    self.state.setGridSize(gridType, previous)
                    break
                previous = size
        else:
            self.multiplyGrid(0.5)

    def multiplyGrid(self, factor):
        gridType = self.adjustor.gridType()
        self.state.setGridSize(gridType, \
                               self.state.getGridSize(gridType) * factor)

    def toggleSnap(self):
        if self.state.snapEnabled:
            self.state.snapEnabled = False
        else:
            self.state.snapEnabled = True
            self.adjustMouseMovement = (0, 0)

    def snapToGrid(self):
        print("Snap to grid")
        axes = self.selectedAxes
        value = list(self.adjustor.getAxes())
        grid = self.state.getGridSize(self.adjustor.gridType())
        value[axes[0]] = round(value[axes[0]] / grid) * grid
        value[axes[1]] = round(value[axes[1]] / grid) * grid
        self.adjustor.setAxes(tuple(value))

    def adjustToOrigin(self):
        print("To origin")
        self.adjustor.setAxes((0.0, 0.0, 0.0))

    def toggleRelativeCoordinates(self):
        if self.state.relativeCoordinatesEnabled:
            self.state.relativeCoordinatesEnabled = False
        else:
            self.state.relativeCoordinatesEnabled = True

    def setAdjustAxisValue(self, axis, number):
        value = list(self.adjustor.getAxes())
        origin = (0, 0, 0)
        if self.state.relativeCoordinatesEnabled:
            origin = self.adjustorOriginalValue
        value[axis] = number + origin[axis]
        self.adjustor.setAxes(tuple(value))
        print(value)

    def completeAdjust(self):
        print("Complete adjust")
        self.inAdjustMode = False
        self.editorMain.unlockMouse()
