__author__ = "vantjac"

from threelib.vectorMath import *
from threelib.mesh import Mesh
from threelib import scripts

class Entity:
    
    def __init__(self, position = ZERO_V, rotation = ZERO_R):
        self.position = position
        self.rotation = rotation
        self.parent = None
        self.children = [ ]

    def setMap(self, gameMap):
        self.gameMap = gameMap
        
    def getPosition(self):
        return self.position

    def getRotation(self):
        return self.rotation
        
    def move(self, translate, rotate):
        self.position = self.position + translate
        self.rotation = self.rotation + rotate

    def getParent(self):
        return self.parent

    def setParent(self, parent):
        self.parent = parent
    
    def getChildren(self):
        return self.children

    def addChild(self, child):
        self.children.append(child)

    def removeChild(self, child):
        self.children.remove(child)

    def update(self, time):
        pass

    def readyToDelete():
        return False


# there are no functions to edit the properties
# values can just be accessed directly
class MeshObject(Entity):
    
    def __init__(self, position = ZERO_V, rotation = ZERO_R, mesh = Mesh()):
        Entity.__init__(self, position, rotation)
        self.mesh = mesh
        
        self.generateRenderMesh = True
        self.blockUseables = True
        self.useEnabled = False
        self.useAction = scripts.EMPTY_SCRIPT
        
        self.generateWalls = True
        self.wallCollideAction = scripts.EMPTY_SCRIPT
        
        self.generateFloor = True
        self.floorCollideAction = scripts.EMPTY_SCRIPT
        
        self.generateVolume = True
        self.volumeStartTouchAction = scripts.EMPTY_SCRIPT
        self.volumeEndTouchAction = scripts.EMPTY_SCRIPT


class Map:
    
    def __init__(self, name):
        self.mapName = name
        
        self.scriptEntityCreators = [ ]
        self.meshObjects = [ ]
        self.camera = None
        self.materials = [ ]
        self.script = scripts.EMPTY_SCRIPT
        self.globalScripts = [ ] # list of file names for script
