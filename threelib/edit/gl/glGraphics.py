__author__ = "vantjac"

from threelib.edit.graphics import GraphicsTools

import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.GLU import *

class GLGraphicsTools(GraphicsTools):
    
    def drawPoint(self, position, color, size):
        glColor(color[0], color[1], color[2])
        glPointSize(size)
        glBegin(GL_POINTS)
        glVertex(position.y, position.z, position.x)
        glEnd()

    def drawMesh(self, mesh):
        glColor(0.8, 0.8, 0.8)
        for f in mesh.getFaces():
            texture = False

            mat = f.getMaterial()
            if mat != None:
                if len(mat.material.texture) != 0:
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

    def drawMeshSelectHull(self, mesh, color):
        glColor(color[0], color[1], color[2])
        for f in mesh.getFaces():
            glBegin(GL_POLYGON)
            for v in f.getVertices():
                pos = v.vertex.getPosition()
                glVertex(pos.y, pos.z, pos.x)
            glEnd()

