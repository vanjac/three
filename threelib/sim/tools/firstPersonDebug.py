__author__ = "jacobvanthoog"

import math
from threelib.sim.base import Entity
from threelib.vectorMath import Vector
from threelib.vectorMath import Rotate

class FirstPersonFlyingPlayer(Entity):

    def __init__(self, world, xLookAxis, yLookAxis, xWalkAxis, yWalkAxis):
        super().__init__()
        self.world = world
        self.xLookAxis = xLookAxis
        self.yLookAxis = yLookAxis
        self.xWalkAxis = xWalkAxis
        self.yWalkAxis = yWalkAxis
        
        self.zVelocity = 0.0
        self.currentFloor = None
        
        self.walkSpeed = 50.0
        
    def scan(self, timeElapsed, totalTime):
        rotation = Rotate(0, float(self.yLookAxis.getChange()), \
                            -float(self.xLookAxis.getChange()))
        translation = Vector(-self.yWalkAxis.getValue(),
                              self.xWalkAxis.getValue()).limitMagnitude(1.0) \
                      *timeElapsed * self.walkSpeed
        
        def do(toUpdateList):
            self.rotation += rotation
            
            # prevent from looking too far up or down
            yRot = self.rotation.y
            if yRot > math.pi/2 and yRot < math.pi:
                self.rotation = self.rotation.setY(math.pi/2)
            if yRot > math.pi and yRot < math.pi*3/2:
                self.rotation = self.rotation.setY(math.pi*3/2)
            
            movement = translation.rotate2(self.rotation.z)
            self.position += movement
        self.actions.addAction(do)

