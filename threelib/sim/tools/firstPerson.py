__author__ = "jacobvanthoog"

import math
from threelib.sim.base import Entity
from threelib.vectorMath import Vector
from threelib.vectorMath import Rotate

class FirstPersonPlayer(Entity):
    GRAVITY = -50.0

    def __init__(self, world, xLookAxis, yLookAxis, xWalkAxis, yWalkAxis):
        super().__init__()
        self.world = world
        self.xLookAxis = xLookAxis
        self.yLookAxis = yLookAxis
        self.xWalkAxis = xWalkAxis
        self.yWalkAxis = yWalkAxis
        
        self.zVelocity = 0.0
        self.currentFloor = None
        
        self.cameraHeight = 16.0
        self.walkSpeed = 50.0
        self.maxWalkAngle = 45.0 # in degrees
        self.maxWalkNormalZ = Vector(1.0, 0.0).rotate2(self.maxWalkAngle).y
        
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
            
            # uphill slopes should slow down movement
            # downhill slopes should speed up movement
            slopeFactor = 1.0
            if self.currentFloor != None:
                if self.currentFloor.isInBounds(self.position):
                    point = self.currentFloor.topPointAt(self.position)
                    if point != None:
                        # this uses vector projection and magic
                        slopeFactor = 1.0 + translation \
                            .rotate2(self.rotation.z).project(point.normal)
            
            previousPosition = self.position
            # walk
            self.position += translation.rotate2(self.rotation.z) * slopeFactor
            if self.currentFloor == None:
                # z velocity
                self.position += Vector(0, 0, self.zVelocity * timeElapsed)
            
            for collision in self.world.collisionMeshes:
                if collision.isEnabled() \
                        and collision.isInBounds(self.position):
                    point = collision.topPointAt(self.position)
                    if point == None:
                        print("Collision error!")
                    else:
                        if self.currentFloor == None:
                            currentZ = self.position.z - self.cameraHeight
                            previousZ = previousPosition.z - self.cameraHeight
                            # if player just hit this floor
                            if currentZ <= point.height \
                                    and previousZ > point.height:
                                self.zVelocity = 0.0
                                self.currentFloor = collision
                        else: # already on a floor
                            # this check is REQUIRED
                            if collision.isInBounds(previousPosition):
                                currentFloorPreviousZ = self.currentFloor \
                                    .topPointAt(previousPosition).height
                                currentFloorCurrentZ = self.currentFloor \
                                    .topPointAt(self.position).height
                                nextFloorPreviousZ = collision \
                                    .topPointAt(previousPosition).height
                                nextFloorCurrentZ = point.height
                                # allow walking from one floor onto another
                                if currentFloorPreviousZ >= nextFloorPreviousZ \
                                  and currentFloorCurrentZ < nextFloorCurrentZ:
                                    self.zVelocity = 0.0
                                    self.currentFloor = collision
            
            if self.currentFloor != None:
                if self.currentFloor.isInBounds(self.position):
                    point = self.currentFloor.topPointAt(self.position)
                    if point == None:
                        print("Collision error!")
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
        

