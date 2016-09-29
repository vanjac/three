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

