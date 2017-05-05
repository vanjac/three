__author__ = "jacobvanthoog"

from threelib.app import AppInterface
from threelib.run.runner import GameRunner
import threelib.world
from threelib.sim.input import SimpleAxisInput
from threelib.sim.input import SimpleButtonInput
from threelib.run.controller import GameController
from threelib import files

import time

unshiftedChars = { '~': '`', '!': '1', '@': '2', '#': '3', '$': '4', '%': '5',
         '^': '6', '&': '7', '*': '8', '(': '9', ')': '0', '_': '-', '+': '=',
         '{': '[', '}': ']', '|': '\\',':': ';', '"': "'", '<': ',', '>': '.',
         '?': '/' }

def unshift(char):
    if char.isalpha():
        return char.lower()
    elif char in unshiftedChars:
        return unshiftedChars[char]
    else:
        return char


class GameInterface(AppInterface, GameController):

    def __init__(self, state):
        GameController.__init__(self)
        self.instance = None
        self.world = None
        self.initialState = state

        self.mouseLocked = False

        self.gameConfig = files.readGameConfig()

    def init(self):
        self.mouseXInput = SimpleAxisInput()
        self.mouseYInput = SimpleAxisInput()

        self.mouseLeftInput = SimpleButtonInput()
        self.mouseMiddleInput = SimpleButtonInput()
        self.mouseRightInput = SimpleButtonInput()

        self.instance.lockMouse()
        self.mouseLocked = True

        self.setState(self.initialState)

    def setState(self, state):
        if self.world is not None:
            self.world.simulator.end()
            self.world.simulator.destroy()

        self.world = state.world

        self.keyInputs = { }

        controlLocalDict = dict(locals())
        controlLocalDict['key'] = self._getKeyInput
        controlLocalDict['mouse_x'] = self.mouseXInput
        controlLocalDict['mouse_y'] = self.mouseYInput

        controlLocalDict['mouse_left'] = self.mouseLeftInput
        controlLocalDict['mouse_middle'] = self.mouseMiddleInput
        controlLocalDict['mouse_right'] = self.mouseRightInput

        for specialKey in ['left', 'right', 'down', 'up']:
            controlLocalDict[specialKey] = self._getKeyInput(specialKey)

        exec('from threelib.sim.input import *',
             controlLocalDict, controlLocalDict)

        for buttonName in self.gameConfig['buttons']:
            script = self.gameConfig['buttons'][buttonName]
            button = eval(script, controlLocalDict, controlLocalDict)
            self.world.buttonInputs[buttonName] = button
            controlLocalDict[buttonName] = button
        for axisName in self.gameConfig['axes']:
            script = self.gameConfig['axes'][axisName]
            axis = eval(script, controlLocalDict, controlLocalDict)
            self.world.axisInputs[axisName] = axis
            controlLocalDict[axisName] = axis

        print("Building world...")
        threelib.world.buildWorld(state)
        print("Done building world")

        self.world.simulator.init()
        self.world.simulator.start()
        self.world.simulator.update()

        self.runner = GameRunner(self.world.simulator, time.time())

    def getRunner(self):
        return self.runner

    def draw(self):
        self.runner.tick(time.time())
        self._removeDeadObjects(self.world.renderMeshes)
        self._removeDeadObjects(self.world.rayCollisionMeshes)
        self._removeDeadObjects(self.world.collisionMeshes)
        self._removeDeadObjects(self.world.skyRenderMeshes)
        self._removeDeadObjects(self.world.directionalLights)
        self._removeDeadObjects(self.world.positionalLights)
        self._removeDeadObjects(self.world.spotLights)
        if self._isDead(self.world.skyCamera):
            self.world.skyCamera = None

    def _removeDeadObjects(self, l):
        toRemove = [ ]
        for simObject in l:
            if simObject.readyToRemove():
                toRemove.append(simObject)
        for simObject in toRemove:
            l.remove(simObject)

    def _isDead(self, simObject):
        if simObject is not None:
            return simObject.readyToRemove()
        return False

    def setAppInstance(self, instance):
        self.instance = instance


    def _getKeyInput(self, char):
        if char in self.keyInputs:
            return self.keyInputs[char]
        else:
            button = SimpleButtonInput()
            self.keyInputs[char] = button
            return button

    def keyPressed(self, key):
        if key[0] == 27: # escape
            self.mouseLocked = False
            self.instance.unlockMouse()

        try:
            char = unshift(key.decode("utf-8"))
        except UnicodeDecodeError:
            # happens when fn + volume change keys are used, for example
            return
        if char in self.keyInputs:
            self.keyInputs[char].setPressed(True)

    def keyReleased(self, key):
        try:
            char = unshift(key.decode("utf-8"))
        except UnicodeDecodeError:
            # happens when fn + volume change keys are used, for example
            return
        if char in self.keyInputs:
            self.keyInputs[char].setPressed(False)

    def specialKeyPressed(self, key):
        if key in self.keyInputs:
            self.keyInputs[key].setPressed(True)

    def specialKeyReleased(self, key):
        if key in self.keyInputs:
            self.keyInputs[key].setPressed(False)

    def mousePressed(self, button, mouseX, mouseY):
        self.instance.lockMouse()
        self.mouseLocked = True

        buttonInput = self._inputForMouseButtonCode(button)
        if buttonInput is not None:
            buttonInput.setPressed(True)

    def mouseReleased(self, button, mouseX, mouseY):
        buttonInput = self._inputForMouseButtonCode(button)
        if buttonInput is not None:
            buttonInput.setPressed(False)

    def _inputForMouseButtonCode(self, code):
        if code == 0:
            return self.mouseLeftInput
        if code == 1:
            return self.mouseMiddleInput
        if code == 2:
            return self.mouseRightInput

    def mouseMoved(self, mouseX, mouseY, pmouseX, pmouseY):
        if self.mouseLocked:
            self.mouseXInput.changeValue(mouseX - pmouseX)
            self.mouseYInput.changeValue(mouseY - pmouseY)

