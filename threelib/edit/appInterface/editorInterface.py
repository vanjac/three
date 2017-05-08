__author__ = "jacobvanthoog"

import math
import numbers

from threelib.edit.editorActions import EditorActions
from threelib.edit.state import *
from threelib.vectorMath import Vector
from threelib.vectorMath import Rotate
import threelib.vectorMath as vectorMath
from threelib.app import AppInterface
from threelib.edit.toolbar import *

MATH_SYMBOLS = ['.', '+', '-', '*', '/', '(', ')']

class EditorInterface(EditorActions, AppInterface):

    def __init__(self, mapPath, state=None):
        super().__init__(mapPath, state)
        self.currentCommand = ""

        self.statusBarHeight = 16

        self.toolbarWidth = 256
        self.toolbarGroups = [ ]

        self.toolbarMouseX = -1
        self.toolbarMouseY = -1
        self.toolbarHoverButton = None
        self.toolbarSelectButton = None

        self._setupToolbar()

    def _setupToolbar(self):
        self.generalGroup = Group("General")
        self.toolbarGroups.append(self.generalGroup)
        self._setupToolbarGeneral(self.generalGroup)

        self.newGroup = Group("New")
        self.toolbarGroups.append(self.newGroup)
        self._setupToolbarNew(self.newGroup)

        self.adjustGroup = Group("Adjust")
        self.toolbarGroups.append(self.adjustGroup)
        self._setupToolbarAdjust(self.adjustGroup)

        self.objectsGroup = Group("Objects")
        self.toolbarGroups.append(self.objectsGroup)
        self._setupToolbarObjects(self.objectsGroup)

        self.facesGroup = Group("Faces")
        self.toolbarGroups.append(self.facesGroup)
        self._setupToolbarFaces(self.facesGroup)

        self.verticesGroup = Group("Vertices")
        self.toolbarGroups.append(self.verticesGroup)
        self._setupToolbarVertices(self.verticesGroup)

    def _updateToolbar(self):
        if self.inAdjustMode:
            for group in self.toolbarGroups:
                group.shown = False
        else:
            self.generalGroup.shown = True
            self.newGroup.shown = True
            self.adjustGroup.shown = True

            enabledStyle = Style((255, 159, 63))
            disabledStyle = Style((127, 127, 127))
            if self.state.selectMode == EditorState.SELECT_OBJECTS:
                self.objectsGroup.shown = True
                self.facesGroup.shown = True
                self.verticesGroup.shown = False
                self.objectModeButton.style = enabledStyle
                self.faceModeButton.style = disabledStyle
                self.vertexModeButton.style = disabledStyle
            elif self.state.selectMode == EditorState.SELECT_FACES:
                self.objectsGroup.shown = False
                self.facesGroup.shown = True
                self.verticesGroup.shown = False
                self.objectModeButton.style = disabledStyle
                self.faceModeButton.style = enabledStyle
                self.vertexModeButton.style = disabledStyle
            elif self.state.selectMode == EditorState.SELECT_VERTICES:
                self.objectsGroup.shown = False
                self.facesGroup.shown = False
                self.verticesGroup.shown = True
                self.objectModeButton.style = disabledStyle
                self.faceModeButton.style = disabledStyle
                self.vertexModeButton.style = enabledStyle

            selectAll = False
            if self.state.selectMode == EditorState.SELECT_OBJECTS:
                if len(self.state.selectedObjects) == 0:
                    selectAll = True
            elif self.state.selectMode == EditorState.SELECT_FACES:
                if len(self.state.selectedFaces) == 0:
                    selectAll = True
            elif self.state.selectMode == EditorState.SELECT_VERTICES:
                if len(self.state.selectedVertices) == 0:
                    selectAll = True
            self.selectAllButton.text = "Select All" if selectAll \
                else "Select None"

    def _setupToolbarGeneral(self, group):
        fileRow = Row()
        group.addRow(fileRow)

        fileRow.addButton(
            Button(text="Save", x=0, width=1, keyboardShortcut="`",
                   action=self.saveFile))

        modeRow = Row()
        group.addRow(modeRow)

        def objectMode():
            self.selectMode(EditorState.SELECT_OBJECTS)
        self.objectModeButton = modeRow.addButton(
            Button(text="Objects", x=0, width=1/3, keyboardShortcut="mo",
                   action=objectMode))
        def faceMode():
            self.selectMode(EditorState.SELECT_FACES)
        self.faceModeButton = modeRow.addButton(
            Button(text="Faces", x=1/3, width=1/3, keyboardShortcut="mf",
                   action=faceMode))
        def vertexMode():
            self.selectMode(EditorState.SELECT_VERTICES)
        self.vertexModeButton = modeRow.addButton(
            Button(text="Vertices", x=2/3, width=1/3, keyboardShortcut="mv",
                   action=vertexMode))

        selectRow = Row()
        group.addRow(selectRow)

        self.selectAllButton = selectRow.addButton(
            Button(text="Select All/None", x=0, width=1, keyboardShortcut="a",
                   action=self.selectAll))

        propertiesRow = Row()
        group.addRow(propertiesRow)

        propertiesRow.addButton(
            Button(text="Properties", x=0, width=0.5, keyboardShortcut="\r",
                   action=self.editPropertiesOfSelected))

        propertiesRow.addButton(
            Button(text="Update", x=0.5, width=0.5, keyboardShortcut="u",
                   action=self.updateSelected))

    def _setupToolbarObjects(self, group):
        generalRow = Row()
        group.addRow(generalRow)

        generalRow.addButton(
            Button(text="Delete", x=0, width=0.5, keyboardShortcut="\b",
                   action=self.deleteSelected))
        generalRow.addButton(
            Button(text="Duplicate", x=0.5, width=0.5, keyboardShortcut="c",
                   action=self.duplicateSelected))

        tieRow = Row()
        group.addRow(tieRow)

        tieRow.addButton(
            Button(text="Set Parent", x=0, width=0.5, keyboardShortcut="t",
                   action=self.setParent))
        tieRow.addButton(
            Button(text="Clear Parent", x=0.5, width=0.5, keyboardShortcut="T",
                   action=self.clearParent))

        selectTieRow1 = Row()
        group.addRow(selectTieRow1)

        selectTieRow1.addButton(
            Button(text="Parent", x=0, width=0.5, keyboardShortcut=",",
                   action=self.selectParent))
        selectTieRow1.addButton(
            Button(text="Children", x=0.5, width=0.5,
                   keyboardShortcut=".", action=self.selectChildren))

        selectTieRow2 = Row()
        group.addRow(selectTieRow2)

        def addParent():
            self.selectParent(addToSelection=True)
        selectTieRow2.addButton(
            Button(text="+ Parent", x=0, width=0.5, keyboardShortcut="<",
                   action=addParent))
        def addChildren():
            self.selectChildren(addToSelection=True)
        selectTieRow2.addButton(
            Button(text="+ Children", x=0.5, width=0.5,
                   keyboardShortcut=">", action=addChildren))

        meshRow = Row()
        group.addRow(meshRow)

        meshRow.addButton(
            Button(text="Clip", x=0, width=0.5, keyboardShortcut="k",
                   action=self.clip))

        meshRow.addButton(
            Button(text="Carve", x=0.5, width=0.5, keyboardShortcut="K",
                   action=self.carve))

    def _setupToolbarNew(self, group):
        newRow = Row()
        group.addRow(newRow)

        newRow.addButton(
            Button(text="Box", x=0, width=0.5, keyboardShortcut="nb",
                   action=self.createBox))
        newRow.addButton(
            Button(text="Point", x=0.5, width=0.5, keyboardShortcut="np",
                   action=self.createPoint))

        newLightRow = Row()
        group.addRow(newLightRow)

        newLightRow.addButton(
            Button(text="Light", x=0, width=1/3,
                   keyboardShortcut="nlp", action=self.createPositionalLight))
        newLightRow.addButton(
            Button(text="Direction", x=1/3, width=1/3,
                   keyboardShortcut="nld", action=self.createDirectionalLight))
        newLightRow.addButton(
            Button(text="Spot", x=2/3, width=1/3,
                   keyboardShortcut="nls", action=self.createSpotLight))

        importRow = Row()
        group.addRow(importRow)

        def importMesh(command):
            if command[-1] != '\r':
                return False
            self.importMesh(command[2:-1])
            return True
        importRow.addButton(
            Button(text="Import Mesh", x=0, width=1, keyboardShortcut="im",
                   action=importMesh, requireKeyboard=True))

    def _setupToolbarAdjust(self, group):
        adjustRow = Row()
        group.addRow(adjustRow)

        adjustRow.addButton(
            Button(text="Translate", x=0, width=1/3, keyboardShortcut="g",
                   action=self.translateSelected))
        adjustRow.addButton(
            Button(text="Origin", x=1/3, width=1/3, keyboardShortcut="o",
                   action=self.adjustOriginOfSelected))
        adjustRow.addButton(
            Button(text="Rotate", x=2/3, width=1/3, keyboardShortcut="r",
                   action=self.rotateSelected))

        scaleRow = Row()
        group.addRow(scaleRow)

        def scale(c):
            if len(c) == 1:
                return False
            last = c[len(c) - 1]
            if last == '\r':
                edges = [0, 0, 0]
                for command in c[1:-1]:
                    # x axis:
                    if command == 'e':  # east
                        edges[0] = 1
                    if command == 'w':  # west
                        edges[0] = -1
                    # y axis:
                    if command == 'n':  # north
                        edges[1] = 1
                    if command == 's':  # south
                        edges[1] = -1
                    # z axis:
                    if command == 't':  # top
                        edges[2] = 1
                    if command == 'b':  # bottom
                        edges[2] = -1

                resize = c[0] == 's'
                self.scaleSelected(tuple(edges), resize)
                return True
            elif last != 'e' and last != 'w' and last != 'n' and last != 's' \
                    and last != 't' and last != 'b':
                print("Invalid command", c)
                return True
            else:
                return False
        scaleRow.addButton(
            Button(text="Resize", x=0, width=0.5, keyboardShortcut="s",
                   action=scale, requireKeyboard=True))
        scaleRow.addButton(
            Button(text="Scale", x=0.5, width=0.5, keyboardShortcut="S",
                   action=scale, requireKeyboard=True))

    def _setupToolbarVertices(self, group):
        vertexRow = Row()
        group.addRow(vertexRow)

        vertexRow.addButton(
            Button(text="Divide Edge", x=0, width=0.5, keyboardShortcut="d",
                   action=self.divideEdge))

        vertexRow.addButton(
            Button(text="Join Vertices", x=0.5, width=0.5, keyboardShortcut="D",
                   action=self.combineVertices))

        edgeRow = Row()
        group.addRow(edgeRow)

        edgeRow.addButton(
            Button(text="Make Edge", x=0, width=0.5, keyboardShortcut="e",
                   action=self.makeEdge))

        edgeRow.addButton(
            Button(text="Combine Faces", x=0.5, width=0.5, keyboardShortcut="E",
                   action=self.combineFaces))

    def _setupToolbarFaces(self, group):
        extrudeRow = Row()
        group.addRow(extrudeRow)

        extrudeRow.addButton(
            Button(text="Extrude", x=0, width=1, keyboardShortcut='h',
                   action=self.extrude))

        materialRow = Row()
        group.addRow(materialRow)

        def setMaterial(command):
            if command[-1] != '\r':
                return False
            self.setCurrentMaterial(command[1:-1])
            return True
        materialRow.addButton(
            Button(text="Set Paint", x=0, width=0.5, keyboardShortcut="P",
                   action=setMaterial, requireKeyboard=True))

        materialRow.addButton(
            Button(text="Paint", x=0.5, width=0.5, keyboardShortcut="p",
                   action=self.paint))

        materialTransformRow = Row()
        group.addRow(materialTransformRow)

        materialTransformRow.addButton(
            Button(text="Translate", x=0, width=1/3, keyboardShortcut="fg",
                   action=self.translateMaterials))

        materialTransformRow.addButton(
            Button(text="Rotate", x=1/3, width=1/3, keyboardShortcut="fr",
                   action=self.rotateMaterials))

        materialTransformRow.addButton(
            Button(text="Scale", x=2/3, width=1/3, keyboardShortcut="fs",
                   action=self.scaleMaterials))


    def setAppInstance(self, instance):
        self.editorMain = instance

    def escape(self):
        super().escape()
        self.currentCommand = ""

    def keyPressed(self, key):
        if key[0] == 27: # escape
            self.escape()
        elif self.movingCamera:
            if key == b'w':
                self.fly = self.fly.setX(-1)
            if key == b's':
                self.fly = self.fly.setX(1)
            if key == b'a':
                self.fly = self.fly.setY(-1)
            if key == b'd':
                self.fly = self.fly.setY(1)
            if key == b'q':
                self.fly = self.fly.setZ(-1)
            if key == b'e':
                self.fly = self.fly.setZ(1)
            if key == b'=':
                self.flySpeed *= 1.5
            if key == b'-':
                self.flySpeed /= 1.5
        else:
            character = chr(key[0])
            if character == '\x7f': # backspace on some platforms, delete on others
                character = '\b'
            if character == '\b' and len(self.currentCommand) != 0:
                # delete from command
                self.currentCommand = self.currentCommand[:-1]
            else:
                # add to command
                self.currentCommand += character

            if len(self.currentCommand) == 0:
                return

            if self.inAdjustMode:
                if self.evaluateAdjustCommand(self.currentCommand):
                    self.currentCommand = ""
                return

            foundMatch = False
            for group in self.toolbarGroups:
                for row in group.rows:
                    for button in row.buttons:
                        buttonCommand = button.keyboardShortcut
                        if buttonCommand == "":
                            continue
                        if buttonCommand == self.currentCommand or \
                                self.currentCommand.startswith(buttonCommand):
                            foundMatch = True
                            if button.keyboardAction is not None:
                                if button.keyboardAction(self.currentCommand):
                                    self.currentCommand = ""
                            elif button.mousePressedAction is not None:
                                button.mousePressedAction()
                                self.currentCommand = ""
                        elif buttonCommand.startswith(self.currentCommand):
                            foundMatch = True
            if not foundMatch:
                print("Unrecognized command " + self.currentCommand)
                self.currentCommand = ""

    def keyReleased(self, key):
        if self.movingCamera:
            if key == b'w':
                self.fly = self.fly.setX(0)
            if key == b's':
                self.fly = self.fly.setX(0)
            if key == b'a':
                self.fly = self.fly.setY(0)
            if key == b'd':
                self.fly = self.fly.setY(0)
            if key == b'q':
                self.fly = self.fly.setZ(0)
            if key == b'e':
                self.fly = self.fly.setZ(0)


    def evaluateAdjustCommand(self, c):

        if c[0] == '\r':
            self.completeAdjust()
            return True

        if c[0] == 'x':
            self.selectAdjustAxis(EditorActions.X)
            return True
        if c[0] == 'y':
            self.selectAdjustAxis(EditorActions.Y)
            return True
        if c[0] == 'z':
            self.selectAdjustAxis(EditorActions.Z)
            return True

        if c[0] == '[':
            self.decreaseGrid()
            return True
        if c[0] == ']':
            self.increaseGrid()
            return True
        if c[0] == 's':
            self.toggleSnap()
            return True
        if c[0] == 'a':
            self.snapToGrid()
            return True
        if c[0] == 'o':
            self.adjustToOrigin()
            return True
        if c[0] == 'r':
            self.toggleRelativeCoordinates()
            return True
        if c[0] == 'l':
            self.toggleAxisLock()
            return True
        if c[0] == 'c':
            self.adjustToCreatePosition()
            return True
        if c[0] == 'g':
            if len(c) == 1 or c[-1].isdigit() or c[-1] == '.':
                return False
            elif c[-1] == '\r' and len(c) > 2:
                self.setGrid(float(c[1:-1]))
                return True
            else:
                print("Invalid command", c)
                return True
        if c[0].isdigit() or c[0] in MATH_SYMBOLS:
            if c[-1].isdigit() or c[-1] in MATH_SYMBOLS:
                return False
            axisChar = c[-1].lower()
            try:
                number = eval(c[:-1])
                if not isinstance(number, numbers.Number):
                    print("Invalid command", c)
                    print(str(number), "is not a number")
                    return True
            except BaseException as e:
                print("Invalid command", c)
                print(e)
                return True
            if axisChar == 'x':
                self.setAdjustAxisValue(EditorActions.X, number)
            elif axisChar == 'y':
                self.setAdjustAxisValue(EditorActions.Y, number)
            elif axisChar == 'z':
                self.setAdjustAxisValue(EditorActions.Z, number)
            else:
                print("Invalid command", c)
            return True

        # if no match
        print("Unrecognized command", c)
        return True


    # mouse buttons: left=0, middle=1, right=2,
    #   scroll-up=3, scroll-down=4, scroll-left=5, scroll-right=6
    def mousePressed(self, button, mouseX, mouseY):
        if button == 0:
            if self.inAdjustMode:
                self.completeAdjust()
            elif self.movingCamera:
                pass
            elif self.toolbarMouseX > 0:
                if self.toolbarHoverButton is not None:
                    self.toolbarSelectButton = self.toolbarHoverButton
                    self.editorMain.lockMouse()
                    if self.toolbarSelectButton.mousePressedAction is not None:
                        self.toolbarSelectButton.mousePressedAction()
                    elif self.toolbarSelectButton.keyboardAction is not None:
                        self.currentCommand = \
                            self.toolbarSelectButton.keyboardShortcut
                        if self.toolbarSelectButton.keyboardAction(
                                self.currentCommand):
                            self.currentCommand = ""
                            self.toolbarSelectButton = None
            else: # select
                multiple = self.editorMain.shiftPressed()
                self.selectAtCursor(multiple)
        if button == 0 or button == 2:
            if self.movingCamera:
                self.movingCamera = False
                self.fly = Vector(0, 0, 0)
                if not self.inAdjustMode:
                    self.editorMain.unlockMouse()
            elif button == 2:
                self.movingCamera = True
                self.editorMain.lockMouse()
        if button == 3:
            self.flySpeed *= 1.1
        if button == 4:
            self.flySpeed /= 1.1

    def mouseReleased(self, button, mouseX, mouseY):
        if self.toolbarSelectButton is not None:
            if not self.inAdjustMode:
                self.editorMain.unlockMouse()
            if self.toolbarSelectButton.mouseReleasedAction is not None:
                self.toolbarSelectButton.mouseReleasedAction()
            self.toolbarSelectButton = None

    def mouseMoved(self, mouseX, mouseY, pmouseX, pmouseY):
        if self.movingCamera:
            movement = Rotate(0,
                              -float(mouseY - pmouseY) * self.lookSpeed,
                              float(mouseX - pmouseX) * self.lookSpeed)
            self.state.cameraRotation += movement
            # prevent from looking too far up or down
            yRot = self.state.cameraRotation.y
            if math.pi/2 < yRot < math.pi:
                self.state.cameraRotation = self.state.cameraRotation.setY(
                    math.pi/2)
            if math.pi < yRot < math.pi*3/2:
                self.state.cameraRotation = self.state.cameraRotation.setY(
                    math.pi*3/2)
        elif self.inAdjustMode:
            self.mouseMovedAdjustMode(mouseX, mouseY, pmouseX, pmouseY)
        elif self.toolbarSelectButton is not None:
            if self.toolbarSelectButton.mouseDraggedAction is not None:
                self.toolbarSelectButton.mouseDraggedAction(
                    mouseX - pmouseX, mouseY - pmouseY)
        else:
            self.toolbarMouseX = mouseX - self.editorMain.windowWidth() \
                                 + self.toolbarWidth
            self.toolbarMouseY = self.editorMain.windowHeight() - mouseY

    def mouseMovedAdjustMode(self, mouseX, mouseY, pmouseX, pmouseY):
        grid = float(self.state.getGridSize(self.adjustor.gridType()))
        mouseGrid = self.adjustMouseGrid

        mouseXDiff = mouseX - pmouseX
        mouseYDiff = -mouseY + pmouseY # up should be positive

        change = [0.0, 0.0] # change in first / second axes

        if self.state.snapEnabled:
            mouseMovement = list(self.adjustMouseMovement)
            mouseMovement[0] += mouseXDiff
            mouseMovement[1] += mouseYDiff
            if mouseMovement[0] > mouseGrid:
                change[0] = math.floor(mouseMovement[0] / mouseGrid)\
                            * grid
                mouseMovement[0] %= mouseGrid
            if mouseMovement[0] < -mouseGrid:
                change[0] = -math.floor(-mouseMovement[0] / mouseGrid)\
                            * grid
                mouseMovement[0] = -(-mouseMovement[0] % mouseGrid)
            if mouseMovement[1] > mouseGrid:
                change[1] = math.floor(mouseMovement[1] / mouseGrid)\
                            * grid
                mouseMovement[1] %= mouseGrid
            if mouseMovement[1] < -mouseGrid:
                change[1] = -math.floor(-mouseMovement[1] / mouseGrid)\
                            * grid
                mouseMovement[1] = -(-mouseMovement[1] % mouseGrid)
            self.adjustMouseMovement = tuple(mouseMovement)
        else:
            change[0] = float(mouseXDiff) / float(mouseGrid) * grid
            change[1] = float(mouseYDiff) / float(mouseGrid) * grid

        if self.state.axisLockEnabled:
            value = list(self.adjustor.getAxes())
            value[0] += change[0]
            value[1] += change[0]
            value[2] += change[0]
            self.adjustor.setAxes(tuple(value))
        else:
            # 0 - 3
            # 0 is looking down -x, 1 is looking down +y,
            # 2 is looking down +x, 3 is looking down -y
            quarter = round(self.state.cameraRotation.z / (math.pi / 2)) % 4

            # 0 - 3
            # 0 is towards -x/+y, 1 is towards +x/+y,
            # 2 is towards +x/-y, 3 is towards -x/-y
            quadrant = math.floor(self.state.cameraRotation.z / (math.pi / 2))

            axes = self.selectedAxes
            if axes[0] > axes[1]: # put axes in order
                axes = (axes[1], axes[0])

            if axes[0] == EditorActions.X and axes[1] == EditorActions.Y:
                if quarter == 0:
                    axes = (EditorActions.Y, EditorActions.X)
                    change[1] = -change[1]
                if quarter == 1:
                    pass
                if quarter == 2:
                    axes = (EditorActions.Y, EditorActions.X)
                    change[0] = -change[0]
                if quarter == 3:
                    change[0] = -change[0]
                    change[1] = -change[1]
            elif axes[0] == EditorActions.X:
                if quadrant == 2 or quadrant == 3:
                    change[0] = -change[0]
            elif axes[0] == EditorActions.Y:
                if quadrant == 1 or quadrant == 2:
                    change[0] = -change[0]

            # looking up reverses y mouse movement
            if axes[1] != EditorActions.Z \
                    and self.state.cameraRotation.y < math.pi:
                change[1] = -change[1]

            value = list(self.adjustor.getAxes())
            value[axes[0]] += change[0]
            value[axes[1]] += change[1]

            self.adjustor.setAxes(tuple(value))


    def getStatusBar(self):
        text = ""

        if self.inAdjustMode:
            if self.movingCamera:
                text += "Fly | "
            else:
                text += self.adjustor.getDescription() + " | "
            value = self.adjustor.getAxes()
            if self.state.relativeCoordinatesEnabled:
                origin = self.adjustorOriginalValue
                value = (value[0]-origin[0],
                         value[1]-origin[1],
                         value[2]-origin[2])
            text += vectorMath.tripleTupleToString(value)
            if self.state.relativeCoordinatesEnabled:
                text += " relative | "
            else:
                text += " absolute | "
            for a in self.selectedAxes:
                if a == EditorActions.X:
                    text += "X"
                if a == EditorActions.Y:
                    text += "Y"
                if a == EditorActions.Z:
                    text += "Z"
            text += " Grid: " + str(self.state.getGridSize(
                self.adjustor.gridType())) + " | "
            if self.state.snapEnabled:
                text += "Snap | "
            else:
                text += "Free | "
            if self.state.axisLockEnabled:
                text += "Lock    | "
            else:
                text += "No lock | "
        else: # not in adjust mode
            if self.movingCamera:
                text += "Fly | "
            else:

                if self.state.selectMode == EditorState.SELECT_OBJECTS:
                    num = len(self.state.selectedObjects)
                    if num == 0:
                        text += "Object select | "
                    elif num == 1:
                        text += "1 object  | "
                        o = self.state.selectedObjects[0]
                        text += o.getType() + ": \"" + o.getName() + "\" | "
                        text += "Pos: " + str(o.getPosition()) + " "
                        text += "Rot: " + str(o.getRotation()) + " "
                        text += "Dim: " + str(o.getDimensions()) + " | "
                    else:
                        text += str(num) + " objects | "
                elif self.state.selectMode == EditorState.SELECT_FACES:
                    num = len(self.state.selectedFaces)
                    if num == 0:
                        text += "Face select | "
                    elif num == 1:
                        text += "1 face  | "
                        f = self.state.selectedFaces[0].face
                        text += "Mat: " + self.getMaterialName(f.getMaterial())\
                                + " "
                        text += "Shift: " + vectorMath.doubleTupleToString(
                            f.textureShift.getTuple()) + " "
                        text += "Rot: " + str(f.textureRotate) + " "
                        text += "Scale: " + vectorMath.doubleTupleToString(
                            f.textureScale.getTuple()) + " | "
                    else:
                        text += str(num) + " faces | "
                elif self.state.selectMode == EditorState.SELECT_VERTICES:
                    num = len(self.state.selectedVertices)
                    if num == 0:
                        text += "Vertex select | "
                    elif num == 1:
                        text += "1 vertex   | "
                        selectedVertex = self.state.selectedVertices[0]
                        position = selectedVertex.vertex.getPosition() + \
                                   selectedVertex.editorObject.getPosition()
                        text += "Pos: " + str(position) + " | "
                    else:
                        text += str(num) + " vertices | "

                text += "Paint: " + self.getMaterialName(
                    self.state.currentMaterial) + " | "
                text += "Create: " + str(self.state.createPosition) + " | "

        if self.currentCommand == "":
            if self.movingCamera:
                text += "WASDQE: fly; click: exit; scroll or -/=: change speed"
            elif self.inAdjustMode:
                text += "Click: complete"
        else:
            text += self.currentCommand

        return text

    def getMaterialName(self, material):
        if material is None:
            return "none"
        else:
            return material.getName().split("/")[-1]

