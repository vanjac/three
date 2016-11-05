__author__ = "jacobvanthoog"

import math

from threelib.edit.base import MeshObject
from threelib.edit.base import PointObject
from threelib.edit.base import stringToBoolean

import threelib.sim.base
from threelib.sim.base import Entity
from threelib.sim.graphics import RenderMesh
from threelib.sim.rayCollision import RayCollisionMesh
from threelib.sim.playerPhysics import CollisionMesh

import threelib.script
      
        
class SolidMeshObject(MeshObject):

    def __init__(self, scale=1):
        super().__init__(scale)
        
        # properties:
        self.constructor = ""
        self.script = "\n\n"
        
        self.generateVisibleMesh = True
        self.visible = True
        
        self.generateRayCollision = True
        self.rayCollisionEnabled = True
        self.useAction = ""
        
        self.generateCollision = True
        self.collisionEnabled = True
        self.isSolid = True
        self.wallCollideAction = ""
        self.floorStartTouchAction = ""
        self.floorEndTouchAction = ""
        self.ceilingCollideAction = ""
    
    def addToWorld(self, world):
        threelib.script.runScript(self.script)
        entity = threelib.script.setVariable(self.constructor,
                                             self.getName())
        if entity == None:
            entity = Entity()
            threelib.script.setVariableValue(self.getName(), entity)
        
        world.simulator.addObject(entity)
        
        if self.generateVisibleMesh:
            renderMesh = RenderMesh(self.getMesh())
            renderMesh.setVisible(self.visible)
            
            world.simulator.addObject(renderMesh)
            world.renderMeshes.append(renderMesh)
            entity.addChild(renderMesh)
        
        if self.generateRayCollision:
            rayCollisionMesh = RayCollisionMesh(self.getMesh())
            rayCollisionMesh.setEnabled(self.rayCollisionEnabled)
            def useAction():
                threelib.script.runScript(self.useAction)
            rayCollisionMesh.setUseAction(useAction)
            
            world.simulator.addObject(rayCollisionMesh)
            world.rayCollisionMeshes.append(rayCollisionMesh)
            entity.addChild(rayCollisionMesh)
        
        if self.generateCollision:
            collisionMesh = CollisionMesh(self.getMesh())
            collisionMesh.setEnabled(self.collisionEnabled)
            collisionMesh.setSolid(self.isSolid)
            def wallCollideAction():
                threelib.script.runScript(self.wallCollideAction)
            collisionMesh.setWallCollideAction(wallCollideAction)
            def floorStartTouchAction():
                threelib.script.runScript(self.floorStartTouchAction)
            collisionMesh.setFloorStartTouchAction(floorStartTouchAction)
            def floorEndTouchAction():
                threelib.script.runScript(self.floorEndTouchAction)
            collisionMesh.setFloorEndTouchAction(floorEndTouchAction)
            def ceilingCollideAction():
                threelib.script.runScript(self.ceilingCollideAction)
            collisionMesh.setCeilingCollideAction(ceilingCollideAction)
            
            world.simulator.addObject(collisionMesh)
            world.collisionMeshes.append(collisionMesh)
            entity.addChild(collisionMesh)
        
        
        entity.translate(self.getPosition())
        entity.rotate(self.getRotation())
        
        return entity
        
    def getProperties(self):
        props = super().getProperties()
        props.update({ "constructor" : self.constructor,
                       "script" : self.script,
                       "generateVisibleMesh" : str(self.generateVisibleMesh),
                       "visible" : str(self.visible),
                       
                       "generateRayCollision" : str(self.generateRayCollision),
                       "rayCollisionEnabled" : str(self.rayCollisionEnabled),
                       "useAction" : self.useAction,
                       
                       "generateCollision" : str(self.generateCollision),
                       "collisionEnabled" : str(self.collisionEnabled),
                       "isSolid" : str(self.isSolid),
                       "wallCollideAction" : self.wallCollideAction,
                       "floorStartTouchAction" : self.floorStartTouchAction,
                       "floorEndTouchAction" : self.floorEndTouchAction,
                       "ceilingCollideAction" : self.ceilingCollideAction
                     })
        return props
        
    def setProperties(self, properties):
        super().setProperties(properties)
        for key, value in properties.items():
            if key == "constructor":
                self.constructor = value
            if key == "script":
                self.script = value
            
            if key == "generateVisibleMesh":
                self.generateVisibleMesh = stringToBoolean(value)
            if key == "visible":
                self.visible = stringToBoolean(value)
            
            if key == "generateRayCollision":
                self.generateRayCollision = stringToBoolean(value)
            if key == "rayCollisionEnabled":
                self.rayCollisionEnabled = stringToBoolean(value)
            if key == "useAction":
                self.useAction = value
            
            if key == "generateCollision":
                self.generateCollision = stringToBoolean(value)
            if key == "collisionEnabled":
                self.collisionEnabled = stringToBoolean(value)
            if key == "isSolid":
                self.isSolid = stringToBoolean(value)
            if key == "wallCollideAction":
                self.wallCollideAction = value
            if key == "floorStartTouchAction":
                self.floorStartTouchAction = value
            if key == "floorEndTouchAction":
                self.floorEndTouchAction = value
            if key == "ceilingCollideAction":
                self.ceilingCollideAction = value
                
    def clone(self):
        clone = SolidMeshObject()
        self.addToClone(clone)
        return clone

    def addToClone(self, clone):
        super().addToClone(clone)
        
        clone.constructor = self.constructor
        clone.script = self.script
        
        clone.generateVisibleMesh = self.generateVisibleMesh
        clone.visible = self.visible
        
        clone.generateRayCollision = self.generateRayCollision
        clone.rayCollisionEnabled = self.rayCollisionEnabled
        clone.useAction = self.useAction
        
        clone.generateCollision = self.generateCollision
        clone.collisionEnabled = self.collisionEnabled
        clone.isSolid = self.isSolid
        clone.wallCollideAction = self.wallCollideAction
        clone.floorStartTouchAction = self.floorStartTouchAction
        clone.floorEndTouchAction = self.floorEndTouchAction
        clone.ceilingCollideAction = self.ceilingCollideAction


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
        if entity == None:
            entity = Entity()
            threelib.script.setVariableValue(self.getName(), entity)
        
        entity.translate(self.getPosition())
        entity.rotate(self.getRotation())
        
        world.simulator.addObject(entity)
        
        if self.getName() == "cam":
            world.camera = entity
        
        return entity

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


class DirectionalLightObject(ScriptPointObject):

    def __init__(self):
        super().__init__()
        
        # properties
        self.constructor = "Light()"
        self.ambient = (0.0, 0.0, 0.0)
        self.diffuse = (1.0, 1.0, 1.0)
        self.specular = (1.0, 1.0, 1.0)
    
    def addToWorld(self, world):
        light = super().addToWorld(world)
        light.setAmbient(self.ambient)
        light.setDiffuse(self.diffuse)
        light.setSpecular(self.specular)
        world.directionalLights.append(light)
        return light

    def getProperties(self):
        props = super().getProperties()
        props.update({ "ambient" : str(self.ambient),
                       "diffuse" : str(self.diffuse),
                       "specular" : str(self.specular)
                      })
        return props
        
    def setProperties(self, properties):
        super().setProperties(properties)
        for key, value in properties.items():
            if key == "ambient":
                self.ambient = threelib.sim.base.stringToTripleTuple(value)
            if key == "diffuse":
                self.diffuse = threelib.sim.base.stringToTripleTuple(value)
            if key == "specular":
                self.specular = threelib.sim.base.stringToTripleTuple(value)
    
    def clone(self):
        clone = DirectionalLightObject()
        self.addToClone(clone)
        return clone

    def addToClone(self, clone):
        super().addToClone(clone)
        
        clone.ambient = self.ambient
        clone.diffuse = self.diffuse
        clone.specular = self.specular


class PositionalLightObject(DirectionalLightObject):

    def __init__(self):
        super().__init__()
        
        # properties
        self.constructor = "PositionalLight()"
        self.attenuationConstant = 0.0
        self.attenuationLinear = 0.0
        self.attenuationQuadratic = 1.0
    
    def addToWorld(self, world):
        light = ScriptPointObject.addToWorld(self, world)
        light.setAmbient(self.ambient)
        light.setDiffuse(self.diffuse)
        light.setSpecular(self.specular)
        light.setAttenuation(self.attenuationConstant,
                             self.attenuationLinear,
                             self.attenuationQuadratic)
        world.positionalLights.append(light)
        return light

    def getProperties(self):
        props = super().getProperties()
        props.update({ "attenuationConstant" : str(self.attenuationConstant),
                       "attenuationLinear" : str(self.attenuationLinear),
                       "attenuationQuadratic" : str(self.attenuationQuadratic)
                      })
        return props
        
    def setProperties(self, properties):
        super().setProperties(properties)
        for key, value in properties.items():
            if key == "attenuationConstant":
                self.attenuationConstant = float(value)
            if key == "attenuationLinear":
                self.attenuationLinear = float(value)
            if key == "attenuationQuadratic":
                self.attenuationQuadratic = float(value)
    
    def clone(self):
        clone = PositionalLightObject()
        self.addToClone(clone)
        return clone

    def addToClone(self, clone):
        super().addToClone(clone)
        
        clone.attenuationConstant = self.attenuationConstant
        clone.attenuationLinear = self.attenuationLinear
        clone.attenuationQuadratic = self.attenuationQuadratic


class SpotLightObject(PositionalLightObject):

    def __init__(self):
        super().__init__()
        
        # properties
        self.constructor = "SpotLight()"
        self.exponent = 0.0
        self.cutoff = 45.0
    
    def addToWorld(self, world):
        light = ScriptPointObject.addToWorld(self, world)
        light.setAmbient(self.ambient)
        light.setDiffuse(self.diffuse)
        light.setSpecular(self.specular)
        light.setAttenuation(self.attenuationConstant,
                             self.attenuationLinear,
                             self.attenuationQuadratic)
        light.setExponent(self.exponent)
        light.setCutoff(math.radians(self.cutoff))
        world.spotLights.append(light)
        return light

    def getProperties(self):
        props = super().getProperties()
        props.update({ "exponent" : str(self.exponent),
                       "cutoff" : str(self.cutoff),
                      })
        return props
        
    def setProperties(self, properties):
        super().setProperties(properties)
        for key, value in properties.items():
            if key == "exponent":
                self.exponent = float(value)
            if key == "cutoff":
                self.cutoff = float(value)
    
    def clone(self):
        clone = SpotLightObject()
        self.addToClone(clone)
        return clone

    def addToClone(self, clone):
        super().addToClone(clone)
        
        clone.exponent = self.exponent
        clone.cutoff = self.cutoff

