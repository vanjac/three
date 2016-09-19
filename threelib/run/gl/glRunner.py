__author__ = "jacobvanthoog"

from threelib.run.appInterface.gameInterface import GameInterface\

import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class GLRunner(GameInterface):

    def __init__(self, state=None):
        super().__init__(state)
        print("OpenGL 1 Game Runner")
        
    def init(self):
        self.instance.updateMaterials(self.world)
        pass
        
    def draw(self):
        pass

