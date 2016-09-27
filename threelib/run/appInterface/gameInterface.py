__author__ = "jacobvanthoog"

from threelib.app import AppInterface
from threelib.run.runner import GameRunner
import threelib.world
from threelib.sim.input import SimpleAxisInput

import time

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
        
    # called by interface implementation every draw
    def step(self):
        self.runner.tick(time.time())

    def setAppInstance(self, instance):
        self.instance = instance

    def keyPressed(self, key):
        pass
    
    def keyReleased(self, key):
        pass
        
    def mousePressed(self, button, mouseX, mouseY):
        pass
        
    def mouseReleased(self, button, mouseX, mouseY):
        pass
    
    def mouseMoved(self, mouseX, mouseY, pmouseX, pmouseY):
        self.mouseXInput.changeValue(mouseX - pmouseX)
        self.mouseYInput.changeValue(mouseY - pmouseY)

