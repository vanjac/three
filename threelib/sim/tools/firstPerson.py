__author__ = "jacobvanthoog"

import math
from threelib.sim.base import Entity
from threelib.vectorMath import Vector
from threelib.vectorMath import Rotate
from threelib.sim.input import ButtonInput

class FirstPersonPlayer(Entity):
    GRAVITY = -80.0

    def __init__(self, world, xLookAxis, yLookAxis, xWalkAxis, yWalkAxis,
                 jumpButton):
        super().__init__()
        self.world = world
        self.xLookAxis = xLookAxis
        self.yLookAxis = yLookAxis
        self.xWalkAxis = xWalkAxis
        self.yWalkAxis = yWalkAxis
        self.jumpButton = jumpButton
        
        self.zVelocity = 0.0
        self.currentFloor = None
        
        self.cameraHeight = 16.0
        self.playerHeight = 20.0
        self.walkSpeed = 50.0
        self.fallMoveSpeed = 30.0
        self.maxWalkAngle = 45.0 # in degrees
        self.maxWalkNormalZ = Vector(1.0, 0.0).rotate2(self.maxWalkAngle).y
        self.jumpVelocity = 50.0
        
    def scan(self, timeElapsed, totalTime):
        rotation = Rotate(0, float(self.yLookAxis.getChange()), \
                            -float(self.xLookAxis.getChange()))
        translation = Vector(-self.yWalkAxis.getValue(),
                              self.xWalkAxis.getValue()).limitMagnitude(1.0) \
                      *timeElapsed * self.walkSpeed
        
        def do(toUpdateList):
            # LOOK
            
            self.rotation += rotation
            
            # prevent from looking too far up or down
            yRot = self.rotation.y
            if yRot > math.pi/2 and yRot < math.pi:
                self.rotation = self.rotation.setY(math.pi/2)
            if yRot > math.pi and yRot < math.pi*3/2:
                self.rotation = self.rotation.setY(math.pi*3/2)
            
            # PHYSICS
            
            if self.currentFloor == None:
                # gravity
                self.zVelocity += FirstPersonPlayer.GRAVITY * timeElapsed
            
            movement = translation.rotate2(self.rotation.z)
            
            # uphill slopes should slow down movement
            # downhill slopes should speed up movement
            slopeFactor = float(self.fallMoveSpeed) / self.walkSpeed
            if self.currentFloor != None:
                if self.currentFloor.isInBounds(self.position):
                    point = self.currentFloor.topPointAt(self.position)
                    if point != None:
                        # if slope is too steep, slide down it
                        if point.normal.z < self.maxWalkNormalZ:
                            movement = point.normal.setZ(0).setMagnitude(1.0)
                        
                        # this uses vector projection and magic
                        slopeFactor = 1.0 + movement.project(point.normal)
                            
            jumpEvent = self.jumpButton.getEvent()
            if self.currentFloor != None:
                if jumpEvent == ButtonInput.PRESSED_EVENT:
                    self.zVelocity = self.jumpVelocity
                    self.currentFloor = None
            
            previousPosition = self.position
            # walk
            self.position += movement * slopeFactor
            if self.currentFloor == None:
                # z velocity
                self.position += Vector(0, 0, self.zVelocity * timeElapsed)
            
            for collision in self.world.collisionMeshes:
                if collision.isEnabled() \
                        and collision.isInBounds(self.position):
                        
                    # check floor collision
                    point = collision.topPointAt(self.position)
                    if point != None:
                        if self.currentFloor == None:
                            # TODO: cleanup!
                            currentZ = self.position.z - self.cameraHeight
                            previousZ = previousPosition.z - self.cameraHeight
                            
                            # if player just hit this floor
                            if currentZ <= point.height \
                                    and previousZ > point.height:
                                self.zVelocity = 0.0
                                self.currentFloor = collision
                            # what if the floor height has changed as the player
                            # moves?
                            nextFloorPreviousPoint = \
                                collision.topPointAt(previousPosition)
                            
                            if nextFloorPreviousPoint != None:
                                if currentZ <= point.height \
                                  and previousZ > nextFloorPreviousPoint.height:
                                    self.zVelocity = 0.0
                                    self.currentFloor = collision
                                
                        # already on a floor
                        elif collision.isInBounds(previousPosition):
                            # these checks are required
                            currentFloorPreviousPoint = self.currentFloor \
                                .topPointAt(previousPosition)
                            currentFloorCurrentPoint = self.currentFloor \
                                .topPointAt(self.position)
                            nextFloorPreviousPoint = \
                                collision.topPointAt(previousPosition)
                            if currentFloorPreviousPoint != None \
                                    and currentFloorCurrentPoint != None \
                                    and nextFloorPreviousPoint != None:
                                currentFloorPreviousZ = \
                                    currentFloorPreviousPoint.height
                                currentFloorCurrentZ = \
                                    currentFloorCurrentPoint.height
                                nextFloorPreviousZ = \
                                    nextFloorPreviousPoint.height
                                nextFloorCurrentZ = point.height
                                # allow walking from one floor onto another
                                if currentFloorPreviousZ >= nextFloorPreviousZ \
                                  and currentFloorCurrentZ < nextFloorCurrentZ:
                                    self.zVelocity = 0.0
                                    self.currentFloor = collision
                    # end check floor collision
                    
                    # check ceiling collision
                    point = collision.bottomPointAt(self.position)
                    if point != None:
                        if self.currentFloor == None:
                            # TODO: cleanup!
                            currentZ = self.position.z - self.cameraHeight \
                                + self.playerHeight
                            previousZ = previousPosition.z - self.cameraHeight \
                                + self.playerHeight
                            
                            # if player just hit this ceiling
                            if currentZ >= point.height \
                                    and previousZ < point.height:
                                self.zVelocity = 0.0
                            # what if the ceiling height has changed as the
                            # player moves?
                            ceilingPreviousPoint = \
                                collision.bottomPointAt(previousPosition)
                            
                            if ceilingPreviousPoint != None:
                                if currentZ >= point.height \
                                  and previousZ < ceilingPreviousPoint.height:
                                    self.zVelocity = 0.0
                    # end check ceiling collision
            # end for each collision mesh
            
            if self.currentFloor != None:
                if self.currentFloor.isInBounds(self.position):
                    point = self.currentFloor.topPointAt(self.position)
                    if point == None:
                        self.zVelocity = 0.0
                        self.currentFloor = None
                    else:
                        z = point.height + self.cameraHeight
                        def do(toUpdateList):
                            self.position = self.position.setZ(z)
                        self.actions.addAction(do)
                else:
                    self.zVelocity = 0.0
                    self.currentFloor = None
            
            toUpdateList.append(self)
        self.actions.addAction(do)

