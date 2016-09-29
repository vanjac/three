__author__ = "jacobvanthoog"

import math

from threelib.edit.base import MeshObject
from threelib.edit.base import PointObject
from threelib.edit.base import stringToBoolean

from threelib.sim.graphics import RenderMesh
from threelib.sim.playerPhysics import CollisionMesh

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
        
        self.generateCollision = True
        self.isSolid = True
        self.wallCollideAction = ""
        self.startTouchAction = ""
        self.endTouchAction = ""
    
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
            
        if self.generateCollision:
            collisionMesh = CollisionMesh(self.getMesh())
            renderMesh.addChild(collisionMesh)
            world.simulator.addObject(collisionMesh)
        
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
                       
                       "generateCollision" : str(self.generateCollision),
                       "isSolid" : str(self.isSolid),
                       "wallCollideAction" : self.wallCollideAction,
                       "startTouchAction" : self.startTouchAction,
                       "endTouchAction" : self.endTouchAction,
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
            
            if key == "generateCollision":
                self.generateCollision = stringToBoolean(value)
            if key == "isSolid":
                self.isSolid = stringToBoolean(value)
            if key == "wallCollideAction":
                self.wallCollideAction = value
            if key == "startTouchAction":
                self.startTouchAction = value
            if key == "endTouchAction":
                self.endTouchAction = value
                
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
        
        clone.generateCollision = self.generateCollision
        clone.isSolid = self.isSolid
        clone.wallCollideAction = self.wallCollideAction
        clone.startTouchAction = self.startTouchAction
        clone.endTouchAction = self.endTouchAction


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

