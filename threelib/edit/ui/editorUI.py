__author__ = "vantjac"

import math

from threelib.edit.editorActions import EditorActions
from threelib.edit.state import *
from threelib.vectorMath import Vector
from threelib.vectorMath import Rotate

class EditorUI(EditorActions):

    def __init__(self, editorMain, state=None):
        super().__init__(editorMain, state)
        self.currentCommand = ""

    def escape(self):
        super().escape()
        self.currentCommand = ""

    def keyPressedEvent(self, key):
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
        else:
            character = chr(key[0])
            if character == '\b' and len(self.currentCommand) != 0:
                # delete from command
                self.currentCommand = self.currentCommand[:-1]
            else:
                # add to command
                self.currentCommand += character
            
            if len(self.currentCommand) == 0:
                return
            
            clearCommand = False
            if self.inAdjustMode:
                clearCommand = self.evaluateAdjustCommand(self.currentCommand)
            else:
                clearCommand = self.evaluateCommand(self.currentCommand)
            if clearCommand:
                self.currentCommand = ""

    def keyReleasedEvent(self, key):
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

    # return True to clear current command
    def evaluateCommand(self, c):

        if c[0] == '`':
            self.saveFile()
            return True

        if c[0] == '\r':
            self.editPropertiesOfSelected()
            return True
        
        if c[0] == 'u':
            self.updateSelected()
            return True
        
        if c[0] == '\b' or c[0] == '\x7f': # backspace or delete
            self.deleteSelected()
            return True

        if c[0] == 'm':
            if len(c) == 1:
                return False
            if c[1] == 'o':
                self.selectMode(EditorState.SELECT_OBJECTS)
                return True
            if c[1] == 'f':
                self.selectMode(EditorState.SELECT_FACES)
                return True
            if c[1] == 'v':
                self.selectMode(EditorState.SELECT_VERTICES)
                return True

        if c[0] == 'n':
            if len(c) == 1:
                return False
            if c[1] == 'b':
                self.createBox()
                return True

        if c[0] == 'a':
            self.selectAll()
            return True

        if c[0] == 'c':
            self.duplicateSelected()
            return True

        if c[0] == 'g':
            self.translateSelected()
            return True

        if c[0] == 'o':
            self.adjustOriginOfSelected()
            return True
            
        if c[0] == 'r':
            self.rotateSelected()
            return True

        if c[0] == 's' or c[0] == 'S':
            if len(c) == 1:
                return False
            last = c[len(c) - 1]
            if last == '\r':
                edges = [0, 0, 0]
                for command in c[1:-1]:
                    # x axis:
                    if command == 'e': # east
                        edges[0] = 1
                    if command == 'w': # west
                        edges[0] = -1
                    # y axis:
                    if command == 'n': # north
                        edges[1] = 1
                    if command == 's': # south
                        edges[1] = -1
                    # z axis:
                    if command == 't': # top
                        edges[2] = 1
                    if command == 'b': # bottom
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

        if c[0] == 'd':
            self.divideEdge()
            return True

        if c[0] == 'D':
            self.combineVertices()
            return True

        if c[0] == 'e':
            self.makeEdge()
            return True

        if c[0] == 'E':
            self.combineFaces()
            return True

        if c[0] == 'h':
            self.extrude()
            return True

        if c[0] == 'k':
            self.clip()
            return True

        if c[0] == 'P':
            if c[len(c) - 1] == '\r':
                self.setCurrentMaterial( c[1:-1] )
                return True
            else:
                return False

        if c[0] == 'p':
            self.paint()
            return True

        # if no match
        print("Unrecognized command " + c)
        return True

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
        if c[0] == 'g':
            if len(c) == 1 or c[-1].isdigit() or c[-1] == '.':
                return False
            elif c[-1] == '\r' and len(c) > 2:
                self.setGrid(float(c[1:-1]))
                return True
            else:
                print("Invalid command", c)
                return True
        if c[0].isdigit() or c[0] == '.' or c[0] == '-':
            if c[-1].isdigit() or c[-1] == '.' or c[-1] == '-':
                return False
            axisChar = c[-1].lower()
            try:
                number = float(c[:-1])
            except ValueError:
                print("Invalid command", c)
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
    def mousePressedEvent(self, button, mouseX, mouseY):
        if button == 0:
            if self.inAdjustMode:
                self.completeAdjust()
            elif not self.movingCamera: # select
                multiple = self.editorMain.shiftPressed()
                self.selectAtCursor(multiple)
        if button == 0 or button==2:
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
    
    def mouseReleasedEvent(self, button, mouseX, mouseY):
        pass

    def mouseMovedEvent(self, mouseX, mouseY, pmouseX, pmouseY):
        if self.movingCamera:
            movement = Rotate(0,
                              -float(mouseY - pmouseY) * self.lookSpeed,
                              float(mouseX - pmouseX) * self.lookSpeed)
            self.state.cameraRotation += movement
            # prevent from looking too far up or down
            yRot = self.state.cameraRotation.y
            if yRot > math.pi/2 and yRot < math.pi:
                self.state.cameraRotation = self.state.cameraRotation.setY(
                    math.pi/2)
            if yRot > math.pi and yRot < math.pi*3/2:
                self.state.cameraRotation = self.state.cameraRotation.setY(
                    math.pi*3/2)
        elif self.inAdjustMode:
            self.mouseMovedAdjustMode(mouseX, mouseY, pmouseX, pmouseY)

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
            text += "(" + \
                    ("{0:.2f}".format(value[0])) + "," + \
                    ("{0:.2f}".format(value[1])) + "," + \
                    ("{0:.2f}".format(value[2])) + ")"
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
                        text += "Pos: " + str(f.textureShift) + " "
                        text += "Rot: " + str(f.textureRotate) + " "
                        text += "Scale: " + str(f.textureScale) + " | "
                    else:
                        text += str(num) + " faces | "
                elif self.state.selectMode == EditorState.SELECT_VERTICES:
                    num = len(self.state.selectedVertices)
                    if num == 0:
                        text += "Vertex select | "
                    elif num == 1:
                        text += "1 vertex   | "
                        text += "Pos: " + \
                                str(self.state.selectedVertices[0].vertex \
                                .getPosition()) + " | "
                    else:
                        text += str(num) + " vertices | "
                
                text += "Paint: " + self.getMaterialName(
                    self.state.currentMaterial) + " | "
        
        if self.currentCommand == "":
            if self.movingCamera:
                text += "WASDQE: fly, click: exit, scroll: change speed"
            elif self.inAdjustMode:
                text += "Click: complete"
        else:
            text += self.currentCommand
        
        return text

    def getMaterialName(self, material):
        if material == None:
            return "none"
        else:
            return material.getName().split("/")[-1]
