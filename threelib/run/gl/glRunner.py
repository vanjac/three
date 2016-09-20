__author__ = "jacobvanthoog"

from threelib.run.appInterface.gameInterface import GameInterface

import math

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
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1) # for getting select pixels
                                              # and storing textures
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        self.instance.updateMaterials(self.world)
        
    def draw(self):
        for renderMesh in self.world.renderMeshes:
            glPushMatrix()
            meshTranslate = renderMesh.getPosition()
            meshRotate = renderMesh.getRotation()
            glTranslate(meshTranslate.y, meshTranslate.z, meshTranslate.x)
            glRotate(math.degrees(meshRotate.z), 0, 1, 0)
            glRotate(math.degrees(meshRotate.y), -1, 0, 0)
            glRotate(math.degrees(meshRotate.x), 0, 0, 1)
            
            glColor(0.8, 0.8, 0.8)
            for f in renderMesh.getMesh().getFaces():
                texture = False

                mat = f.getMaterial()
                if mat != None:
                    if mat.isLoaded():
                        texture = True
                        glEnable(GL_TEXTURE_2D)
                        glBindTexture(GL_TEXTURE_2D, mat.getNumber())
                
                glBegin(GL_POLYGON)
                for v in f.getVertices():
                    pos = v.vertex.getPosition()
                    texPos = v.textureVertex
                    glTexCoord(texPos.x, texPos.y)
                    glVertex(pos.y, pos.z, pos.x)
                glEnd()

                if texture:
                    glDisable(GL_TEXTURE_2D)
            
            glPopMatrix()

