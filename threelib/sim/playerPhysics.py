__author__ = "jacobvanthoog"

from threelib.vectorMath import Vector
import threelib.sim.base

class CollisionMesh(threelib.sim.base.Entity):
    """
    A mesh that the player can walk on or collide with
    """
    
    def __init__(self, mesh):
        super().__init__()
        self.mesh = mesh
        self.enabled = True
        self.solid = True
        self.wallCollideAction = None
        self.floorStartTouchAction = None
        self.floorEndTouchAction = None
        self.ceilingCollideAction = None
        
    def getMesh(self):
        """
        The collision mesh.
        """
        return self.mesh
        
    def setMesh(self, mesh):
        """
        Set the mesh. No effect until update().
        """
        def do(toUpdateList):
            self.mesh = mesh
        self.actions.addAction(do)

    def isEnabled(self):
        return self.enabled
        
    def setEnabled(self, enabled):
        def do(toUpdateList):
            self.enabled = enabled
        self.actions.addAction(do)
        
    def isSolid(self):
        return self.solid
    
    def setSolid(self, solid):
        def do(toUpdateList):
            self.solid = solid
        self.actions.addAction(do)

    def getWallCollideAction(self):
        return self.wallCollideAction
    
    def setWallCollideAction(self, action):
        def do(toUpdateList):
            self.wallCollideAction = action
        self.actions.addAction(do)
        
    def getFloorStartTouchAction(self):
        return self.floorStartTouchAction
    
    def setFloorStartTouchAction(self, action):
        def do(toUpdateList):
            self.floorStartTouchAction = action
        self.actions.addAction(do)
        
    def getFloorEndTouchAction(self):
        return self.floorEndTouchAction
    
    def setFloorEndTouchAction(self, action):
        def do(toUpdateList):
            self.floorEndTouchAction = action
        self.actions.addAction(do)
        
    def getCeilingCollideAction(self):
        return self.ceilingCollideAction
    
    def setCeilingCollideAction(self, action):
        def do(toUpdateList):
            self.ceilingCollideAction = action
        self.actions.addAction(do)

