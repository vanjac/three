__author__ = "jacobvanthoog"

from threelib.sim.base import Entity
from threelib.vectorMath import Rotate

class FirstPersonCamera(Entity):
    
    def __init__(self, xLookAxis, yLookAxis):
        super().__init__()
        self.xLookAxis = xLookAxis
        self.yLookAxis = yLookAxis
        
    def scan(self, timeElapsed, totalTime):
        movement = Rotate(0,
                          float(self.yLookAxis.getChange()),
                          -float(self.xLookAxis.getChange()))
        def do(toUpdateList):
            self.rotation += movement
        self.actions.addAction(do)

