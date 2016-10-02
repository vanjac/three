__author__ = "jacobvanthoog"

from threelib.sim.base import Entity
from threelib.vectorMath import Vector
from threelib.vectorMath import Rotate

class FirstPersonCamera(Entity):
    
    def __init__(self, yLookAxis):
        super().__init__()
        self.yLookAxis = yLookAxis
        
    def scan(self, timeElapsed, totalTime):
        movement = Rotate(0, float(self.yLookAxis.getChange()), 0)
        def do(toUpdateList):
            self.rotate(movement)
            toUpdateList.append(self)
        self.actions.addAction(do)

class FirstPersonPlayer(Entity):

    def __init__(self, world, xLookAxis, xWalkAxis, yWalkAxis):
        super().__init__()
        self.world = world
        self.xLookAxis = xLookAxis
        self.xWalkAxis = xWalkAxis
        self.yWalkAxis = yWalkAxis
        
    def scan(self, timeElapsed, totalTime):
        rotation = Rotate(0, 0, -float(self.xLookAxis.getChange()))
        translation = Vector(-self.yWalkAxis.getValue() * timeElapsed,
                              self.xWalkAxis.getValue() * timeElapsed)
        def do(toUpdateList):
            self.rotate(rotation)
            self.translate(translation.rotate(self.rotation))
            toUpdateList.append(self)
        self.actions.addAction(do)

