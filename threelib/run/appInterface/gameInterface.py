__author__ = "jacobvanthoog"

from threelib.app import AppInterface
from threelib.run.runner import GameRunner
import threelib.world
from threelib.sim.input import SimpleAxisInput
from threelib.sim.input import SimpleButtonInput

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


class GameInterface(AppInterface):

    def __init__(self, state):
        self.instance = None
        
        print("Building world...")
        threelib.world.buildWorld(state)
        print("Done building world")
        
        self.world = state.world
            
        self.world.simulator.init()
        self.world.simulator.start()
        
        self.runner = GameRunner(self.world.simulator, time.time())
        
        self.mouseXInput = SimpleAxisInput()
        self.mouseYInput = SimpleAxisInput()
        
        self.mouseLeftInput = SimpleButtonInput()
        self.mouseMiddleInput = SimpleButtonInput()
        self.mouseRightInput = SimpleButtonInput()
        
    # called by interface implementation every draw
    def step(self):
        self.runner.tick(time.time())

    def setAppInstance(self, instance):
        self.instance = instance

    def keyPressed(self, key):
        char = unshift(key.decode("utf-8"))
    
    def keyReleased(self, key):
        char = unshift(key.decode("utf-8"))
        
    def mousePressed(self, button, mouseX, mouseY):
        buttonInput = self._inputForMouseButtonCode(button)
        if buttonInput != None:
            buttonInput.setPressed(True)
        
    def mouseReleased(self, button, mouseX, mouseY):
        buttonInput = self._inputForMouseButtonCode(button)
        if buttonInput != None:
            buttonInput.setPressed(False)
        
    def _inputForMouseButtonCode(self, code):
        if code == 0:
            return self.mouseLeftInput
        if code == 1:
            return self.mouseMiddleInput
        if code == 2:
            return self.mouseRightInput
    
    def mouseMoved(self, mouseX, mouseY, pmouseX, pmouseY):
        self.mouseXInput.changeValue(mouseX - pmouseX)
        self.mouseYInput.changeValue(mouseY - pmouseY)

