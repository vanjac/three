__author__ = "jacobvanthoog"

from threelib.app import AppInterface
from threelib.run.runner import GameRunner
import threelib.world
from threelib.sim.input import SimpleAxisInput
from threelib.sim.input import SimpleButtonInput
from threelib.run.controller import GameController

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

        # TODO: remove these once input customization has been added!
        self.world.axisInputs['mouse-x'] = self.mouseXInput
        self.world.axisInputs['mouse-y'] = self.mouseYInput
        self.world.buttonInputs['mouse-left'] = self.mouseLeftInput
        self.world.buttonInputs['mouse-middle'] = self.mouseMiddleInput
        self.world.buttonInputs['mouse-right'] = self.mouseRightInput
        self.world.buttonInputs['w'] = self._getKeyInput('w')
        self.world.buttonInputs['a'] = self._getKeyInput('a')
        self.world.buttonInputs['s'] = self._getKeyInput('s')
        self.world.buttonInputs['d'] = self._getKeyInput('d')
        self.world.buttonInputs['space'] = self._getKeyInput(' ')

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

        char = unshift(key.decode("utf-8"))
        if char in self.keyInputs:
            self.keyInputs[char].setPressed(True)

    def keyReleased(self, key):
        char = unshift(key.decode("utf-8"))
        if char in self.keyInputs:
            self.keyInputs[char].setPressed(False)

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

