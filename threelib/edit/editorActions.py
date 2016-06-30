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
        self.adjustMouseGrid = 24 # number of pixels per grid line

        # flags
        self.selectAtCursorOnDraw = False
        self.selectMultiple = False
    
    
    def saveFile(self):
        print("Saving map... ", end="")
        files.saveMapState(files.getCurrentMap(), self.state)
        print("Done")

    def editPropertiesOfSelected(self):
        if not self.state.selectMode == EditorState.SELECT_OBJECTS:
            print("Only objects have properties")
        elif len(self.state.selectedObjects) == 0:
            print("Nothing selected")
        elif len(self.state.selectedObjects) > 1:
            print("Cannot edit properties of multiple objects")
        else:
            print("Edit object properties")
            props = self.state.selectedObjects[0].getProperties()
            text = ""
            for key, value in props.items():
                multiLine = '\n' in value
                if multiLine:
                    text += key + ":\n" + value + "\n~~~\n"
                else:
                    text += key + "=" + value + "\n"
            files.openProperties(text)

    def updateSelected(self):
        if not self.state.selectMode == EditorState.SELECT_OBJECTS:
            print("Only objects can be updated")
        elif len(self.state.selectedObjects) == 0:
            print("Nothing selected")
        elif len(self.state.selectedObjects) > 1:
            print("Cannot update multiple objects")
        else:
            print("Update object")
            text = files.readProperties()
            props = { }
            inMultiLine = False
            multiLineKey = ""
            multiLineValue = ""
            for line in text.split('\n'):
                if not inMultiLine:
                    line = line.strip()
                    if line == '':
                        pass
                    elif '=' in line:
                        key, value = line.split('=')
                        props[key] = value
                    elif line.endswith(':'):
                        inMultiLine = True
                        multiLineKey = line[:-1]
                        multiLineValue = ""
                    else:
                        print("Could not parse line:")
                        print(line)
                        print("Stopping")
                        return
                else: # in multi line
                    if line == "~~~":
                        inMultiLine = False
                        props[multiLineKey] = multiLineValue
                    else:
                        multiLineValue += line + "\n"
            if inMultiLine:
                print("Unclosed multi-line value!")
                print("Stopping")
                return
            
            self.state.selectedObjects[0].setProperties(props)

    def deleteSelected(self):
        if not self.state.selectMode == EditorState.SELECT_OBJECTS:
            print("Only objects can be deleted")
        elif len(self.state.selectedObjects) == 0:
            print("Nothing selected")
        else:
            print("Delete selected objects")
            for o in self.state.selectedObjects:
                o.removeFromParent()
                self.state.objects.remove(o)
            self.state.deselectAll()

    def duplicateSelected(self):
        if not self.state.selectMode == EditorState.SELECT_OBJECTS:
            print("Only objects can be duplicated")
        elif len(self.state.selectedObjects) == 0:
            print("Nothing selected")
        else:
            print("Duplicate selected objects")
            for o in self.state.selectedObjects:
                self.state.objects.append(o.clone())

            self.translateSelected()

        
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
            else:
                self.state.deselectAll()
        elif self.state.selectMode == EditorState.SELECT_FACES:
            if len(self.state.selectedFaces) == 0:
                for o in self.state.objects:
                    if o.getMesh() != None:
                        for f in o.getMesh().getFaces():
                            self.state.selectedFaces.append(
                                FaceSelection(o, f))
            else:
                self.state.selectedFaces = [ ]
        elif self.state.selectMode == EditorState.SELECT_VERTICES:
            if len(self.state.selectedVertices) == 0:
                for o in self.state.objects:
                    if o.getMesh() != None:
                        for v in o.getMesh().getVertices():
                            self.state.selectedVertices.append(
                                VertexSelection(o, v))
            else:
                self.state.selectedVertices = [ ]

    def translateSelected(self):
        if self.state.selectMode == EditorState.SELECT_OBJECTS:
            if len(self.state.selectedObjects) == 0:
                print("Nothing selected")
            elif len(self.state.selectedObjects) == 1:
                self.setupAdjustMode(TranslateAdjustor(
                    self.state.selectedObjects[0]))
            else:
                adjustors = [ ]
                for o in self.state.selectedObjects:
                    adjustors.append(TranslateAdjustor(o))
                self.setupAdjustMode(MultiTranslateAdjustor(adjustors))
        elif self.state.selectMode == EditorState.SELECT_VERTICES:
            if len(self.state.selectedVertices) == 0:
                print("Nothing selected")
            elif len(self.state.selectedVertices) == 1:
                selected = self.state.selectedVertices[0]
                self.setupAdjustMode(VertexTranslateAdjustor(
                    selected.vertex,
                    selected.editorObject))
            else:
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
                adjustors = [ ]
                for f in self.state.selectedFaces:
                    for v in f.face.getVertices():
                        adjustors.append(VertexTranslateAdjustor(
                            v.vertex,
                            f.editorObject))
                self.setupAdjustMode(MultiTranslateAdjustor(adjustors))

    
    def adjustOriginOfSelected(self):
        if self.state.selectMode == EditorState.SELECT_OBJECTS:
            if len(self.state.selectedObjects) == 0:
                print("Nothing selected")
            elif len(self.state.selectedObjects) == 1:
                print("Change origin of object")
                self.setupAdjustMode(OriginAdjustor(
                    self.state.selectedObjects[0]))
            else:
                print("Change origin of objects")
                adjustors = [ ]
                for o in self.state.selectedObjects:
                    adjustors.append(OriginAdjustor(o))
                self.setupAdjustMode(MultiTranslateAdjustor(adjustors))
        else:
            print("Only objects have origins")
                
                 
    def rotateSelected(self):
        if self.state.selectMode == EditorState.SELECT_OBJECTS:
            if len(self.state.selectedObjects) == 0:
                print("Nothing selected")
            elif len(self.state.selectedObjects) == 1:
                self.setupAdjustMode(RotateAdjustor(
                    self.state.selectedObjects[0]))
            else:
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
                translators = [ ]
                rotators = [ ]
                for f in self.state.selectedFaces:
                    for v in f.face.getVertices():
                        translators.append(VertexTranslateAdjustor(
                            v.vertex,
                            f.editorObject))
                        rotators.append(NoOpAdjustor(Adjustor.ROTATE))
                self.setupAdjustMode(MultiRotateAdjustor(translators, rotators))

    # see ScaleAdjustor for description of edges and resize value
    def scaleSelected(self, edges, resize=False):
        if self.state.selectMode == EditorState.SELECT_OBJECTS:
            if len(self.state.selectedObjects) == 0:
                print("Nothing selected")
            elif len(self.state.selectedObjects) == 1:
                self.setupAdjustMode(ScaleAdjustor(
                    self.state.selectedObjects[0], edges, resize))
            else:
                self.setupAdjustMode(MultiScaleAdjustor(
                    self.state.selectedObjects, edges, resize))
        elif self.state.selectMode == EditorState.SELECT_VERTICES:
            if len(self.state.selectedVertices) == 0:
                print("Nothing selected")
            elif len(self.state.selectedVertices) == 1:
                print("Single vertex cannot be "
                      + "resized" if resize else "scaled")
            else:
                vertices = [ ]
                for v in self.state.selectedVertices:
                    vertices.append(v.vertex)
                self.setupAdjustMode(MultiVertexScaleAdjustor(vertices, edges,
                                                              resize))
        elif self.state.selectMode == EditorState.SELECT_FACES:
            if len(self.state.selectedFaces) == 0:
                print("Nothing selected")
            else:
                vertices = [ ]
                for f in self.state.selectedFaces:
                    for v in f.face.getVertices():
                        vertices.append(v.vertex)
                self.setupAdjustMode(MultiVertexScaleAdjustor(vertices, edges,
                                                              resize))

    def setupAdjustMode(self, adjustor):
        self.inAdjustMode = True
        self.adjustor = adjustor
        self.adjustorOriginalValue = adjustor.getAxes()
        self.adjustMouseMovement = (0, 0)
        self.editorMain.lockMouse()

    def selectAtCursor(self, multiple=False):
        self.selectAtCursorOnDraw = True
        self.selectMultiple = multiple

    
    # Mesh editing:
    
    def divideEdge(self):
        if self.state.selectMode != EditorState.SELECT_VERTICES \
           or len(self.state.selectedVertices) != 2:
            print("2 vertices must be selected")
        else:
            print("Divide edge")
            v1 = self.state.selectedVertices[0].vertex
            v2 = self.state.selectedVertices[1].vertex
            mesh = self.state.selectedVertices[0].editorObject.getMesh()
            
            # faces that have both vertices
            faces = self.findSharedFaces(v1, v2)

            if len(faces) < 2:
                print("Please select the 2 vertices of an edge.")
                print("Stopping")
                return
            if len(faces) > 2:
                print("WARNING: " + len(faces) + " have these vertices!")
                print("This should never happen.")
                # continue and hope it works

            newVertex = MeshVertex( (v1.getPosition() + v2.getPosition()) / 2 )
            mesh.addVertex(newVertex)

            for face in faces:
                index1 = face.indexOf(v1)
                index2 = face.indexOf(v2)
                numVertices = len(face.getVertices())
                
                # index1 should be the lowest
                if index1 > index2:
                    temp = index1
                    index1 = index2
                    index2 = temp
                
                # make sure indices are consecutive
                insertIndex = 0
                if index2 - index1 == 1:
                    insertIndex = index2
                elif index1 == 0 and index2 == numVertices - 1:
                    insertIndex = index1
                else:
                    continue
                
                face.addVertex(newVertex, index=insertIndex)

    
    def makeEdge(self):
        if self.state.selectMode != EditorState.SELECT_VERTICES \
           or len(self.state.selectedVertices) != 2:
            print("2 vertices must be selected")
        else:
            print("Make edge")
            v1 = self.state.selectedVertices[0].vertex
            v2 = self.state.selectedVertices[1].vertex
            mesh = self.state.selectedVertices[0].editorObject.getMesh()
            
            # faces that have both vertices
            faces = self.findSharedFaces(v1, v2)

            if len(faces) != 1:
                print("Please select 2 unconnected vertices on a face.")
                print("Stopping")
                return

            face = faces[0]

            # divide vertices into 2 new faces

            index1 = face.indexOf(v1)
            index2 = face.indexOf(v2)
            numVertices = len(face.getVertices())

            # list of MeshFaceVertices
            face1Vertices = [ ]
            face2Vertices = [ ]

            inFace1 = True

            for i in range(0, numVertices):
                if inFace1:
                    face1Vertices.append(face.getVertices()[i])
                else:
                    face2Vertices.append(face.getVertices()[i])
                if i == index1 or i == index2:
                    inFace1 = not inFace1
                    if inFace1:
                        face1Vertices.append(face.getVertices()[i])
                    else:
                        face2Vertices.append(face.getVertices()[i])

            mesh.removeFace(face)

            newFace1 = MeshFace()
            for v in face1Vertices:
                newFace1.addVertex(v.vertex, v.textureVertex)
            newFace2 = MeshFace()
            for v in face2Vertices:
                newFace2.addVertex(v.vertex, v.textureVertex)
            
            mesh.addFace(newFace1)
            mesh.addFace(newFace2)

    
    def combineVertices(self):
        if self.state.selectMode != EditorState.SELECT_VERTICES \
           or len(self.state.selectedVertices) != 2:
            print("2 vertices must be selected")
        else:
            print("Combine vertices")
            v1 = self.state.selectedVertices[0].vertex
            v2 = self.state.selectedVertices[1].vertex
            mesh = self.state.selectedVertices[0].editorObject.getMesh()
            
            # faces that have both vertices
            sharedFaces = self.findSharedFaces(v1, v2)
            
            # replace all v2 references with v1

            v2References = list(v2.getReferences())
            for face in v2References:
                for vertex in face.getVertices():
                    if vertex.vertex == v2:
                        face.replaceVertex(vertex,
                                           MeshFaceVertex(v1,
                                                          vertex.textureVertex))

            # remove duplicate v1 vertices
            for face in sharedFaces:
                vertexIndex = face.indexOf(v1)
                vertex = face.getVertices()[vertexIndex]
                face.removeVertex(vertex) # remove only first reference
                v1.addReference(face)

            mesh.removeVertex(v2)
            del self.state.selectedVertices[1]

    
    def combineFaces(self):
        if self.state.selectMode != EditorState.SELECT_VERTICES \
           or len(self.state.selectedVertices) != 2:
            print("2 vertices must be selected")
        else:
            print("Combine faces")
            v1 = self.state.selectedVertices[0].vertex
            v2 = self.state.selectedVertices[1].vertex
            mesh = self.state.selectedVertices[0].editorObject.getMesh()
            
            # faces that have both vertices
            faces = self.findSharedFaces(v1, v2)
    
            if len(faces) != 2:
                print("The vertices of an edge dividing 2 faces must be "
                      "selected")
                print("Stopping")
                return

            newFace = MeshFace()
            
            faceNum = 0
            for face in faces:
                numVertices = len(face.getVertices())
                v1Index = face.indexOf(v1)
                v2Index = face.indexOf(v2)
                # make sure there are vertices moving from v1 to v2
                # otherwise swap them
                if v1Index - v2Index != 1 and \
                   not (v2Index == numVertices - 1 and v1Index == 0):
                    temp = v1Index
                    v1Index = v2Index
                    v2Index = temp

                i = v1Index
                while i != v2Index:
                    newVertex = face.getVertices()[i]
                    newFace.addVertex(newVertex.vertex, newVertex.textureVertex)
                    i += 1
                    i %= numVertices

                faceNum += 1
            
            mesh.removeFace(faces[0])
            mesh.removeFace(faces[1])
            mesh.addFace(newFace)
                

    # find faces that have both vertices
    def findSharedFaces(self, v1, v2):
        faces = list(v1.getReferences())

        faces2 = v2.getReferences()
        remove = [ ]
        for face in faces:
            if face not in faces2:
                remove.append(face)
        for face in remove:
            faces.remove(face)

        return faces
                
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
        self.adjustor.complete()
