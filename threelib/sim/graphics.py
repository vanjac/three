__author__ = "jacobvanthoog"

import threelib.sim.base

class RenderMesh(threelib.sim.base.Entity):
    """
    A mesh that is shown in the game.
    """

    def __init__(self, mesh):
        super().__init__()
        self.mesh = mesh
        self.visible = True
        self.staticMesh = True

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

    def meshIsStatic(self):
        """
        If True, the mesh should never change.
        """
        return self.staticMesh

    def setMeshIsStatic(self, static):
        """
        Set whether the mesh will never change. No effect until update().
        """
        def do(toUpdateList):
            self.staticMesh = static
        self.actions.addAction(do)
