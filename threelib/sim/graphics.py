__author__ = "jacobvanthoog"

import threelib.sim.base.Entity

class RenderMesh(Entity):
    """
    A mesh that is shown in the game.
    """
    
    def __init__(self, mesh):
        super().__init__()
        self.mesh = mesh
        self.blockUseables = True
        self.useAction = None
        self.visible = True
        
    def getMesh(self):
        """
        The mesh that is rendered.
        """
        return self.mesh
        
    def setMesh(self, mesh):
        """
        Set the mesh. No effect until update().
        """
        def do(toUpdateList):
            self.mesh = mesh
        self.actions.addAction(do)
        
    def blocksUseables(self):
        """
        If True (default), the player will not be able to "use" objects hidden
        behind this one, even if the RenderMesh is not visible. This must be
        True in order for the useAction to have any effect.
        """
        return self.blockUseables
        
    def setBlockUseables(self, enabled):
        """
        Set whether the RenderMesh should block useables (see
        ``blocksUseables()``). No effect until update().
        """
        def do(toUpdateList):
            self.blockUseables = enabled
        self.actions.addAction(do)
        
    def isVisible(self):
        """
        If False, the mesh will not be drawn.
        """
        return self.visible
        
    def setVisible(self, visible):
        """
        Set whether the mesh is drawn. No effect until update().
        """
        def do(toUpdateList):
            self.visible = visible
        self.actions.addAction(do)
        
    def getUseAction(self):
        """
        Get the action that is run when this mesh is "used" (clicked or
        otherwise activated) by the player. Returns a function with no arguments
        or return value.
        """
        return self.useAction
        
    def setUseAction(self, action):
        """
        Set the function to run when this mesh is "used." Should be a function
        with no arguments or return value. No effect until update().
        """
        def do(toUpdateList):
            self.useAction = action
        self.actions.addAction(do)
