__author__ = "jacobvanthoog"

import threelib.sim.base

class RayCollisionMesh(threelib.sim.base.Entity):
    """
    A mesh that rays (like the one to detect usable objects) can collide with
    """

    def __init__(self, mesh):
        super().__init__()
        self.mesh = mesh
        self.enabled = True
        self.useAction = None

    def getMesh(self):
        """
        The mesh that rays collide with.
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
        """
        If False, rays will not collide with the mesh.
        """
        return self.enabled

    def setEnabled(self, enabled):
        """
        Set whether to use the mesh to block rays. No effect until update().
        """
        def do(toUpdateList):
            self.enabled = enabled
        self.actions.addAction(do)

    def getUseAction(self):
        """
        Get the action to be run when the player "uses" the object.
        """
        return self.useAction

    def setUseAction(self, action):
        """
        Set the action to be run when the player "uses" the object. No effect
        until update().
        """
        def do(toUpdateList):
            self.useAction = action
        self.actions.addAction(do)

    def doUseAction(self):
        if self.useAction != None:
            self.useAction()

