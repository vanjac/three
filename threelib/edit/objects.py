__author__ = "vantjac"

import math

from threelib.edit.base import MeshObject
from threelib.edit.base import PointObject
from threelib.edit.base import stringToBoolean

from threelib.sim.graphics import RenderMesh

import threelib.script
      
        
class SolidMeshObject(MeshObject):

    def __init__(self, scale=1):
        super().__init__(scale)
        
        # properties:
        self.visible = True
        self.blockUseables = True
        self.useAction = ""
        
        self.generateWalls = True
        self.wallCollideAction = ""
        
        self.generateFloor = True
        self.floorStartTouchAction = ""
        self.floorEndTouchAction = ""
        
        self.generateCeiling = True
        self.ceilingStartTouchAction = ""
        self.ceilingEndTouchAction = ""
        
        self.generateVolume = False
        self.volumeStartTouchAction = ""
        self.volumeEndTouchAction = ""
    
    def addToWorld(self, world):
        renderMesh = RenderMesh(self.getMesh())
        renderMesh.translate(self.getPosition())
        renderMesh.rotate(self.getRotation())
        renderMesh.setVisible(self.visible)
        def useAction():
            exec(self.useAction)
        renderMesh.setUseAction(useAction)
        renderMesh.setBlockUseables(self.blockUseables)
        world.renderMeshes.append(renderMesh)
        
        world.simulator.addObject(renderMesh)
        
        return renderMesh
        
    def getProperties(self):
        props = super().getProperties()
        props.update({ "visible" : str(self.visible),
                       "blockUseables" : str(self.blockUseables),
                       "useAction" : self.useAction,
                       
                       "generateWalls" : str(self.generateWalls),
                       "wallCollideAction" : self.wallCollideAction,
                       
                       "generateFloor" : str(self.generateFloor),
                       "floorStartTouchAction" : self.floorStartTouchAction,
                       "floorEndTouchAction" : self.floorEndTouchAction,
                       
                       "generateCeiling" : str(self.generateCeiling),
                       "ceilingStartTouchAction" : self.ceilingStartTouchAction,
                       "ceilingEndTouchAction" : self.ceilingEndTouchAction,
                       
                       "generateVolume" : str(self.generateVolume),
                       "volumeStartTouchAction" : self.volumeStartTouchAction,
                       "volumeEndTouchAction" : self.volumeEndTouchAction
                     })
        return props
        
    def setProperties(self, properties):
        super().setProperties(properties)
        for key, value in properties.items():
            if key == "visible":
                self.visible = stringToBoolean(value)
            if key == "blockUseables":
                self.blockUseables = stringToBoolean(value)
            if key == "useAction":
                self.useAction = value
            
            if key == "generateWalls":
                self.generateWalls = stringToBoolean(value)
            if key == "wallCollideAction":
                self.wallCollideAction = value
                
            if key == "generateFloor":
                self.generateFloor = stringToBoolean(value)
            if key == "floorStartTouchAction":
                self.floorStartTouchAction = value
            if key == "floorEndTouchAction":
                self.floorEndTouchAction = value
            
            if key == "generateCeiling":
                self.generateCeiling = stringToBoolean(value)
            if key == "ceilingStartTouchAction":
                self.ceilingStartTouchAction = value
            if key == "ceilingEndTouchAction":
                self.ceilingEndTouchAction = value
                
            if key == "generateVolume":
                self.generateVolume = stringToBoolean(value)
            if key == "volumeStartTouchAction":
                self.volumeStartTouchAction = value
            if key == "volumeEndTouchAction":
                self.volumeEndTouchAction = value
                
    def clone(self):
        clone = SolidMeshObject()
        self.addToClone(clone)
        return clone

    def addToClone(self, clone):
        super().addToClone(clone)
        
        clone.visible = self.visible
        clone.blockUseables = self.blockUseables
        clone.useAction = self.useAction
        
        clone.generateWalls = self.generateWalls
        clone.wallCollideAction = self.wallCollideAction
        
        clone.generateFloor = self.generateFloor
        clone.floorStartTouchAction = self.floorStartTouchAction
        clone.floorEndTouchAction = self.floorEndTouchAction
        
        clone.generateCeiling = self.generateCeiling
        clone.ceilingStartTouchAction = self.ceilingStartTouchAction
        clone.ceilingEndTouchAction = self.ceilingEndTouchAction
        
        clone.generateVolume = self.generateVolume
        clone.volumeStartTouchAction = self.volumeStartTouchAction
        clone.volumeEndTouchAction = self.volumeEndTouchAction


class ScriptPointObject(PointObject):

    def __init__(self):
        super().__init__()
        
        # properties
        self.variableName = "" # will be a global that other scripts can access
        self.constructor = ""
        self.script = "\n\n"
    
    def addToWorld(self, world):
        threelib.script.runScript(self.script)
        simObject = threelib.script.setVariable(self.constructor,
                                                self.variableName)
        world.simulator.addObject(simObject)

    def getProperties(self):
        props = super().getProperties()
        props.update({ "variableName" : self.variableName,
                       "constructor" : self.constructor,
                       "script" : self.script
                      })
        return props
        
    def setProperties(self, properties):
        super().setProperties(properties)
        for key, value in properties.items():
            if key == "variableName":
                self.variableName = value
            if key == "constructor":
                self.constructor = value
            if key == "script":
                self.script = value
    
    def clone(self):
        clone = ScriptPointObject()
        self.addToClone(clone)
        return clone

    def addToClone(self, clone):
        super().addToClone(clone)
        
        clone.variableName = self.variableName
        clone.constructor = self.constructor
        clone.script = self.script

