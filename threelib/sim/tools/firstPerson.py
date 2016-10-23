__author__ = "jacobvanthoog"

import math
from threelib.sim.base import Entity
from threelib.vectorMath import Vector
from threelib.vectorMath import Rotate
from threelib import vectorMath
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
        self.playerHeight = 24.0
        self.playerWidth = 14.0
        self.walkSpeed = 50.0
        self.fallMoveSpeed = 30.0
        self.maxWalkAngle = 45.0 # in degrees
        self.minWalkNormalZ = Vector(1.0, 0.0)\
            .rotate2(math.radians(self.maxWalkAngle)).x
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
            sliding = False
            
            # uphill slopes should slow down movement
            # downhill slopes should speed up movement
            slopeFactor = float(self.fallMoveSpeed) / self.walkSpeed
            if self.currentFloor != None:
                point = self._topPoint(self.currentFloor, self.position)
                if point != None:
                    # if slope is too steep, slide down it
                    if point.normal.z < self.minWalkNormalZ:
                        movement = point.normal.setZ(0).setMagnitude(1.0)
                        sliding = True
                    
                    # this uses vector projection and magic
                    slopeFactor = 1.0 + movement.project(point.normal)
                            
            jumpEvent = self.jumpButton.getEvent()
            if self.currentFloor != None:
                if jumpEvent == ButtonInput.PRESSED_EVENT and sliding == False:
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
                        and self._inBounds(collision, self.position) \
                        and collision != self.currentFloor:
                        
                    topPoint = self._topPoint(collision, self.position)
                    bottomPoint = self._bottomPoint(collision, self.position)
                    
                    # check wall collision
                    if (not self._inBounds(collision, previousPosition)) \
                        and vectorMath.rangesIntersect(
                            self._playerBottom(self.position).z,
                            self._playerTop(self.position).z,
                            bottomPoint.height, topPoint.height):
                        self.position = previousPosition.setZ(self.position.z)
                        continue
                    
                        
                    # check floor collision
                    if topPoint != None:
                        if self.currentFloor == None:
                            # TODO: cleanup!
                            currentZ = self._playerBottom(self.position).z
                            previousZ = self._playerBottom(previousPosition).z
                            
                            # if player just hit this floor
                            if currentZ <= topPoint.height \
                                    and previousZ > topPoint.height:
                                self.zVelocity = 0.0
                                self.currentFloor = collision
                            # what if the floor height has changed as the player
                            # moves?
                            nextFloorPreviousPoint = self._topPoint(
                                collision, previousPosition)
                            
                            if nextFloorPreviousPoint != None:
                                if currentZ <= topPoint.height \
                                  and previousZ > nextFloorPreviousPoint.height:
                                    self.zVelocity = 0.0
                                    self.currentFloor = collision
                                
                        # already on a floor
                        elif self._inBounds(collision, previousPosition):
                            # these checks are required
                            currentFloorPreviousPoint = self._topPoint(
                                self.currentFloor, previousPosition)
                            currentFloorCurrentPoint = self._topPoint(
                                self.currentFloor, self.position)
                            nextFloorPreviousPoint = self._topPoint(
                                collision, previousPosition)
                            if currentFloorPreviousPoint != None \
                                    and currentFloorCurrentPoint != None \
                                    and nextFloorPreviousPoint != None:
                                currentFloorPreviousZ = \
                                    currentFloorPreviousPoint.height
                                currentFloorCurrentZ = \
                                    currentFloorCurrentPoint.height
                                nextFloorPreviousZ = \
                                    nextFloorPreviousPoint.height
                                nextFloorCurrentZ = topPoint.height
                                # allow walking from one floor onto another
                                if currentFloorPreviousZ >= nextFloorPreviousZ \
                                  and currentFloorCurrentZ < nextFloorCurrentZ:
                                    # if the new floor's slope is too steep,
                                    # don't walk onto it
                                    if topPoint.normal.z < self.minWalkNormalZ:
                                        self.position = previousPosition \
                                            .setZ(self.position.z)
                                    else:
                                        self.zVelocity = 0.0
                                        self.currentFloor = collision
                    # end check floor collision
                    
                    # check ceiling collision
                    if bottomPoint != None:
                        if self.currentFloor == None:
                            # TODO: cleanup!
                            currentZ = self._playerTop(self.position).z
                            previousZ = self._playerTop(previousPosition).z
                            
                            # if player just hit this ceiling
                            if currentZ >= bottomPoint.height \
                                    and previousZ < bottomPoint.height:
                                self.zVelocity = 0.0
                            # what if the ceiling height has changed as the
                            # player moves?
                            ceilingPreviousPoint = self._bottomPoint(
                                collision, previousPosition)
                            
                            if ceilingPreviousPoint != None:
                                if currentZ >= bottomPoint.height \
                                  and previousZ < ceilingPreviousPoint.height:
                                    self.zVelocity = 0.0
                    # end check ceiling collision
            # end for each collision mesh
            
            if self.currentFloor != None:
                point = self._topPoint(self.currentFloor, self.position)
                if point == None:
                    self.zVelocity = 0.0
                    self.currentFloor = None
                else:
                    z = point.height + self.cameraHeight
                    def do(toUpdateList):
                        self.position = self.position.setZ(z)
                    self.actions.addAction(do)
            
            toUpdateList.append(self)
        self.actions.addAction(do)


    # return a vector that is in bounds, or None
    def _inBounds(self, collision, point):
        if collision.isInBounds(point):
            return point
        else:
            return collision.nearestBoundsPoint(point,
                maxDistance=self.playerWidth/2.0)

    def _topPoint(self, collision, point):
        pointInBounds = self._inBounds(collision, point)
        if pointInBounds == None:
            return None
        else:
            return collision.topPointAt(pointInBounds)

    def _bottomPoint(self, collision, point):
        pointInBounds = self._inBounds(collision, point)
        if pointInBounds == None:
            return None
        else:
            return collision.bottomPointAt(pointInBounds)

    def _playerTop(self, playerPosition):
        return self._playerBottom(playerPosition) \
            + Vector(0, 0, self.playerHeight)
            
    def _playerBottom(self, playerPosition):
        return playerPosition - Vector(0, 0, self.cameraHeight)

