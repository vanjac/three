__author__ = "jacobvanthoog"

from threelib.app import AppInterface


class GameInterface(AppInterface):

    def __init__(self, state):
        self.state = state
        self.instance = None
        print("Game Runner")

    def setAppInstance(self, instance):
        self.instance = instance

    def init(self):
        pass
        
    def draw(self):
        pass

    def keyPressed(self, key):
        pass
    
    def keyReleased(self, key):
        pass
        
    def mousePressed(self, button, mouseX, mouseY):
        pass
        
    def mouseReleased(self, button, mouseX, mouseY):
        pass
    
    def mouseMoved(self, mouseX, mouseY, pmouseX, pmouseY):
        pass
