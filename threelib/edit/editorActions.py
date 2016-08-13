__author__ = "vantjac"

import math

from threelib.edit.state import *
from threelib.vectorMath import Vector
from threelib.vectorMath import Rotate
from threelib.edit.objects import *
from threelib.edit.adjust import *
from threelib.materials import MaterialReference

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
        self.movingCamera = False
        self.lookSpeed = .005
        self.flySpeed = 2.0
        self.fly = Vector(0, 0, 0) # each component can be 0, 1, or -1

        # clip arrow
        self.arrowShown = False
        self.arrowStart = Vector(0, 0, 0)
        self.arrowEnd = Vector(0, 0, 0)

        # adjust mode
        self.inAdjustMode = False
        self.adjustor = None
        self.adjustorOriginalValue = (0.0, 0.0, 0.0)
        self.selectedAxes = (EditorActions.X, EditorActions.Y)
        self.adjustMouseMovement = (0, 0) # in snap mode
        self.adjustMouseGrid = 24 # number of pixels per grid line
        self.adjustCompleteAction = None # function that is run after completion

        # flags
        self.selectAtCursorOnDraw = False
        self.selectMultiple = False
    

    def escape(self):
        self.movingCamera = False
        self.fly = Vector(0, 0, 0)
        self.editorMain.unlockMouse()
        if self.inAdjustMode:
            self.adjustor.setAxes(self.adjustorOriginalValue)
            self.adjustor.cancel()
            self.inAdjustMode = False
            self.adjustor = None
    
    def saveFile(self):
        print("Saving map... ", end="")
        files.saveMapState(files.getCurrentMap(), self.state)
        print("Done")

    def editPropertiesOfSelected(self):
        if not self.state.selectMode == EditorState.SELECT_OBJECTS:
            print("Only objects have properties")
        elif len(self.state.selectedObjects) == 0:
            print("Edit world properties")
            props = self.state.worldObject.getProperties()
            self.makePropsFile(props)
        elif len(self.state.selectedObjects) > 1:
            print("Cannot edit properties of multiple objects")
        else:
            print("Edit object properties")
            props = self.state.selectedObjects[0].getProperties()
            self.makePropsFile(props)

    def makePropsFile(self, props):
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
            print("Update world")
            props = self.readPropsFile()
            if props != None:
                self.state.worldObject.setProperties(props)
        elif len(self.state.selectedObjects) > 1:
            print("Cannot update multiple objects")
        else:
            print("Update object")
            props = self.readPropsFile()
            if props != None:
                self.state.selectedObjects[0].setProperties(props)

    def readPropsFile(self):
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
            return None
        return props

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
        box = MeshObject(self.state.translateGridSize)
        self.createObject(box)

    def createObject(self, newObject):
        self.selectMode(EditorState.SELECT_OBJECTS)
        self.state.deselectAll()
        newObject.setPosition(self.state.createPosition)
        self.state.objects.append(newObject)
        self.state.select(newObject)
        self.setupAdjustMode(TranslateAdjustor(newObject))

        def setCreatePosition():
            self.state.createPosition = \
                Vector.fromTuple(self.adjustor.getAxes())
        self.adjustCompleteAction = setCreatePosition


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

    def extrude(self):
        if self.state.selectMode == EditorState.SELECT_OBJECTS:
            if len(self.state.selectedObjects) == 0:
                print("Nothing selected")
            else:
                adjustors = [ ]
                for o in self.state.selectedObjects:
                    if o.getMesh() != None:
                        for face in o.getMesh().getFaces():
                            adjustors.append(ExtrudeAdjustor(
                                face, o, self.state))
                
                self.setupAdjustMode(MultiExtrudeAdjustor(adjustors))
                
                def deleteHollowedObjects():
                    for o in self.state.selectedObjects:
                        o.removeFromParent()
                        self.state.objects.remove(o)
                    self.state.deselectAll()
                self.adjustCompleteAction = deleteHollowedObjects
        
        elif self.state.selectMode == EditorState.SELECT_VERTICES:
            print("Faces or objects must be selected to extrude")
        elif self.state.selectMode == EditorState.SELECT_FACES:
            if len(self.state.selectedFaces) == 0:
                print("Nothing selected")
            elif len(self.state.selectedFaces) == 1:
                self.setupAdjustMode(ExtrudeAdjustor(
                    self.state.selectedFaces[0].face,
                    self.state.selectedFaces[0].editorObject,
                    self.state))
            else:
                adjustors = [ ]
                for face in self.state.selectedFaces:
                    adjustors.append(ExtrudeAdjustor(
                        face.face,
                        face.editorObject,
                        self.state))
                self.setupAdjustMode(MultiExtrudeAdjustor(adjustors))

    def setupAdjustMode(self, adjustor):
        self.inAdjustMode = True
        self.adjustor = adjustor
        self.adjustorOriginalValue = adjustor.getAxes()
        self.adjustMouseMovement = (0, 0)
        self.editorMain.lockMouse()

    def setupArrowAction(self, action):
        self.arrowStart = self.state.createPosition
        self.arrowEnd = self.arrowStart
        self.arrowShown = True
        self.setupAdjustMode(ArrowStartAdjustor(self))

        def arrowStartSet():
            self.arrowEnd = self.arrowStart
            self.setupAdjustMode(ArrowEndAdjustor(self))
            
            def arrowEndSet():
                self.arrowShown = False
                self.state.createPosition = self.arrowStart
                action()
            self.adjustCompleteAction = arrowEndSet
        self.adjustCompleteAction = arrowStartSet

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
            if mesh != self.state.selectedVertices[1].editorObject.getMesh():
                print("Please select 2 vertices on the same mesh")
                return
            
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


    def clip(self):
        if self.state.selectMode == EditorState.SELECT_OBJECTS:
            if len(self.state.selectedObjects) == 0:
                print("Objects must be selected")
            else:
                self.setupArrowAction(self.clipSelected)
        else:
            print("Objects must be selected")

    def clipSelected(self):
        print("Clip!")
        planePoint = self.arrowStart
        # arrow points in direction of half to remove
        planeNormal = (planePoint - self.arrowEnd).normalize()
        
        for o in self.state.selectedObjects:
            if o.getMesh() != None:
                # translate everything relative to mesh
                relativePoint = planePoint - o.getPosition()
                planeConstants = self.calculatePlaneConstants(relativePoint,
                                                              planeNormal)
                self.clipMesh(o.getMesh(), planeConstants, relativePoint,
                              planeNormal)

    def clipMesh(self, mesh, planeConstants, planePoint, planeNormal):
        INSIDE = 0
        ON_PLANE = 1 # counts as inside
        OUTSIDE = 2
        
        newFaceEdges = [ ] # pairs of vectors
        facesToRemove = [ ]

        for face in mesh.getFaces():
            vertexLocations = [ ] # INSIDE, OUTSIDE, or ON_PLANE
            hasInside = False
            hasOutside = False
            hasOnPlane = False
            for faceVertex in face.getVertices():
                vector = faceVertex.vertex.getPosition()
                if self.vectorIsClose(vector, planePoint):
                    vertexLocations.append(ON_PLANE)
                    hasOnPlane = True
                    continue # to next vertex
                angle = (vector - planePoint).normalize()\
                                             .angleBetween(planeNormal)
                if self.isclose(angle, math.pi / 2): # 90 degrees
                    vertexLocations.append(ON_PLANE)
                    hasOnPlane = True
                elif angle < math.pi / 2:
                    vertexLocations.append(INSIDE)
                    hasInside = True
                else:
                    vertexLocations.append(OUTSIDE)
                    hasOutside = True
            #print(vertexLocations)

            if (not hasInside) and (not hasOutside):
                print("Mesh face and clip plane are coplanar!"
                      "Skipping this mesh.")
                # TODO if some faces have already been clipped they will not be
                # restored if an error like this occurs
                return
            if hasOnPlane:
                # search for edges on the plane and add them to the list
                for i in range(0, len(vertexLocations)):
                    # -1 is a valid index
                    if vertexLocations[i] == ON_PLANE and \
                       vertexLocations[i-1] == ON_PLANE:
                        edge = (face.getVertices()[i].vertex.getPosition(),
                                face.getVertices()[i-1].vertex.getPosition())
                        self.addUniqueEdge(edge, newFaceEdges)
            if not hasInside:
                print("Remove face")
                facesToRemove.append(face) # face is entirely outside plane
                continue # to next face
            
            if hasInside and hasOutside:
                # partly inside plane and partly outside; clip the face
                print("Clip face")

                # rotate/translate both the face and clip plane so the face is
                # at x = 0
                # vertex 0 will be the origin
                origin = face.getVertices()[0].vertex.getPosition()
                faceNormalRotate = face.getNormal().rotation()
                
                translatedPlanePoint = planePoint - origin
                rotatedPlane = self.rotatePlane(translatedPlanePoint,
                                                planeNormal, -faceNormalRotate)
                planeLineConstants = Vector(rotatedPlane[1],
                                            rotatedPlane[2],
                                            rotatedPlane[3])

                # remove vertices outside the clip plane
                verticesToRemove = [ ]
                vertexInsertationIndices = [ ]
                edgesToClip = [ ]
                i = 0
                for location in vertexLocations:
                    if location == OUTSIDE:
                        verticesToRemove.append(face.getVertices()[i].vertex)
                        if vertexLocations[i-1] != OUTSIDE:
                            edge = (face.getVertices()[i].vertex.getPosition(),
                                face.getVertices()[i-1].vertex.getPosition())
                            edgesToClip.append(edge)
                            vertexInsertationIndices.append(i)
                    else:
                        if vertexLocations[i-1] == OUTSIDE:
                            edge = (face.getVertices()[i].vertex.getPosition(),
                                face.getVertices()[i-1].vertex.getPosition())
                            edgesToClip.append(edge)
                            vertexInsertationIndices.append(i)
                    i += 1
                newVertices = [ ]
                # reverse array to prevent lower indices from pushing up higher
                # indices
                for i in reversed(vertexInsertationIndices):
                    newVertex = mesh.addVertex()
                    face.addVertex(newVertex, index=i)
                    newVertices.insert(0, newVertex)
                for v in verticesToRemove:
                    face.removeVertex(face.findFaceVertex(v))

                if len(edgesToClip) != 2:
                    print("WARNING: Not 2 edges to clip for this face!")
                
                # there is a line where the face and the clip plane intersect
                # the face has already been oriented to x=0, so the intersection
                # is easy to calculate: for plane ax+by+cz+d=0, the intersection
                # with x=0 is by+cz+d=0.
                # the edges that cross the clip plane will be clipped by
                # creating new vertices where they intersect the line. the
                # vertices will then be rotated back.
                i = 0
                for edge in edgesToClip:
                    # vector 0 and vector 1 are the two points of the rotated
                    # edge. after rotating the edges, x values for all will be
                    # 0 (not always exact because of float inaccuracies)
                    v0 = (edge[0] - origin).rotate(-faceNormalRotate)
                    v1 = (edge[1] - origin).rotate(-faceNormalRotate)
                    # equation for the line: ax+by+c=0
                    # represented as a Vector of homogeneous coordinates
                    edgeLineConstants = Vector( v0.z - v1.z,
                                                v1.y - v0.y,
                                                v0.y*v1.z - v1.y*v0.z )
                    intersectionPoint = edgeLineConstants.cross(
                        planeLineConstants).homogeneousTo2d()
                    intersectionPoint = Vector(0,
                                               intersectionPoint.x,
                                               intersectionPoint.y)
                    # undo any rotations
                    intersectionPoint = intersectionPoint.inverseRotate(
                        faceNormalRotate) + origin
                    print(edge, intersectionPoint)
                    newVertices[i].setPosition(intersectionPoint)
                    i += 1

        for face in facesToRemove:
            mesh.removeFace(face)

    def rotatePlane(self, point, normal, rotate):
        # return plane constants
        point = point.rotate(rotate)
        normal = normal.rotate(rotate)
        return self.calculatePlaneConstants(point, normal)
    
    def calculatePlaneConstants(self, point, normal):
        # (a, b, c, d)
        # ax + by + cz + d = 0
        return (normal.x, normal.y, normal.z,
                -point.dot(normal))

    # add the edge to the list only if it hasn't already been added
    # check for reverse order of vertices
    def addUniqueEdge(self, edge, edgeList):
        for existingEdge in edgeList:
            if self.vectorIsClose(existingEdge[0], edge[0]) and \
               self.vectorIsClose(existingEdge[1], edge[1]):
                return
            if self.vectorIsClose(existingEdge[0], edge[1]) and \
               self.vectorIsClose(existingEdge[1], edge[0]):
                return
        print("Adding edge")
        edgeList.append(edge)

    # Based on https://www.python.org/dev/peps/pep-0485/
    # Taken from https://github.com/PythonCHB/close_pep/blob/master/isclose.py
    # Python 3.5 has this, but 3.4 doesn't.
    # I changed the default value of abs_tol, and also removed some checking for
    # special cases that will never appear here.
    def isclose(self, a, b, rel_tol=1e-9, abs_tol=1e-9):
        if a == b:
            return True
        if math.isinf(abs(a)) or math.isinf(abs(b)):
            return False
        
        diff = abs(b - a)
        return (((diff <= abs(rel_tol * b)) or
                 (diff <= abs(rel_tol * a))) or
                (diff <= abs_tol))

    def vectorIsClose(self, a, b):
        return self.isclose(a.x, b.x) \
            and self.isclose(a.y, b.y) \
            and self.isclose(a.z, b.z)
        

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
        adjustor = self.adjustor
        if self.adjustCompleteAction != None:
            action = self.adjustCompleteAction
            self.adjustCompleteAction = None
            action()
        adjustor.complete()
        # prevent issues if complete action involves a new adjust mode:
        if adjustor == self.adjustor:
            self.adjustor = None


    # MATERIALS:

    def setCurrentMaterial(self, name):
        if name != None and name != "":
            foundMaterial = self.state.world.findMaterial(name)
        
            if foundMaterial != None:
                self.state.setCurrentMaterial(foundMaterial)
                self.state.world.updateMaterial(self.state.currentMaterial)
            else:
                matRef = MaterialReference(name)
                self.state.world.addMaterial(matRef)
                self.state.setCurrentMaterial(matRef)
        else:
            self.state.world.updateMaterial(self.state.currentMaterial)
        
        self.state.currentMaterial.load()

    def paint(self):
        if self.state.selectMode == EditorState.SELECT_OBJECTS:
            if len(self.state.selectedObjects) == 0:
                print("Nothing selected")
            else:
                for o in self.state.selectedObjects:
                    if o.getMesh() != None:
                        for f in o.getMesh().getFaces():
                            self.setFaceMaterial(f, self.state.currentMaterial)
        elif self.state.selectMode == EditorState.SELECT_VERTICES:
            print("Cannot paint vertices")
        elif self.state.selectMode == EditorState.SELECT_FACES:
            if len(self.state.selectedFaces) == 0:
                print("Nothing selected")
            else:
                for f in self.state.selectedFaces:
                    self.setFaceMaterial(f.face, self.state.currentMaterial)

    def setFaceMaterial(self, face, materialReference):
        if face.getMaterial() != None:
            self.state.world.removeMaterialReference(face.getMaterial())
        
        face.setMaterial(materialReference)
        
        if face.getMaterial() != None:
            face.getMaterial().addReference()
