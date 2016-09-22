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
        self.constructor = ""
        self.script = "\n\n"
        
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
        threelib.script.runScript(self.script)
        entity = threelib.script.setVariable(self.constructor,
                                             self.getName())
        
        renderMesh = RenderMesh(self.getMesh())
        
        if entity != None:
            entity.translate(self.getPosition())
            entity.rotate(self.getRotation())
            entity.addChild(renderMesh)
            world.simulator.addObject(entity)
        
        renderMesh.translate(self.getPosition())
        renderMesh.rotate(self.getRotation())
        renderMesh.setVisible(self.visible)
        def useAction():
            threelib.script.runScript(self.script)
        renderMesh.setUseAction(useAction)
        renderMesh.setBlockUseables(self.blockUseables)
        world.renderMeshes.append(renderMesh)
        
        world.simulator.addObject(renderMesh)
        
        if entity != None:
            return entity
        else:
            return renderMesh
        
    def getProperties(self):
        props = super().getProperties()
        props.update({ "constructor" : self.constructor,
                       "script" : self.script,
                       "visible" : str(self.visible),
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
            if key == "constructor":
                self.constructor = value
            if key == "script":
                self.script = value
            
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
        
        clone.constructor = self.constructor
        clone.script = self.script
        
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
        self.constructor = ""
        self.script = "\n\n"
    
    def addToWorld(self, world):
        threelib.script.runScript(self.script)
        entity = threelib.script.setVariable(self.constructor,
                                                self.getName())
        if entity != None:
            entity.translate(self.getPosition())
            entity.rotate(self.getRotation())
            
            world.simulator.addObject(entity)
            
            if self.getName() == "cam":
                world.camera = entity

    def getProperties(self):
        props = super().getProperties()
        props.update({ "constructor" : self.constructor,
                       "script" : self.script
                      })
        return props
        
    def setProperties(self, properties):
        super().setProperties(properties)
        for key, value in properties.items():
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
        
        clone.constructor = self.constructor
        clone.script = self.script

