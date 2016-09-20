__author__ = "jacobvanthoog"

from threelib.app import AppInterface
import threelib.world


class GameInterface(AppInterface):

    def __init__(self, state):
        self.instance = None
        
        print("Building world...")
        threelib.world.buildWorld(state)
        print("Done building world")
        
        self.world = state.world
        
        # temporary fix
        for renderMesh in self.world.renderMeshes:
            renderMesh.update()
        

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
        pass
