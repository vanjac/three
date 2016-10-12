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
        
    def scan(self, timeElapsed, totalTime):
        self.zVelocity += FirstPersonPlayer.GRAVITY * timeElapsed
    
        rotation = Rotate(0, float(self.yLookAxis.getChange()), \
                            -float(self.xLookAxis.getChange()))
        translation = Vector(-self.yWalkAxis.getValue() * timeElapsed,
                              self.xWalkAxis.getValue() * timeElapsed)
        def do(toUpdateList):
            self.rotation += rotation
            
            # prevent from looking too far up or down
            yRot = self.rotation.y
            if yRot > math.pi/2 and yRot < math.pi:
                self.rotation = self.rotation.setY(math.pi/2)
            if yRot > math.pi and yRot < math.pi*3/2:
                self.rotation = self.rotation.setY(math.pi*3/2)
            
            self.position += translation.rotate2(self.rotation.z)
            self.position += Vector(0, 0, self.zVelocity * timeElapsed)
            toUpdateList.append(self)
        self.actions.addAction(do)
        
        for collision in self.world.collisionMeshes:
            if collision.isInBounds(self.position):
                point = collision.topPointAt(self.position)
                if point == None:
                    print("Collision error!")
                else:
                    z = point.height + 16
                    def do(toUpdateList):
                        self.position = self.position.setZ(z)
                    self.actions.addAction(do)

