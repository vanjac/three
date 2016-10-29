__author__ = "jacobvanthoog"

from threelib.run.appInterface.gameInterface import GameInterface
from threelib.world import RayCollisionRequest

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
        super().init()
        
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1) # for getting select pixels
                                              # and storing textures
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        self.instance.updateMaterials(self.world)
        
    def draw(self):
        super().draw()
        
        # Ray collisions
        while self.world.hasRayCollisionRequest():
            request = self.world.nextRayCollisionRequest()
            
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            if request.nearClip != None and request.farClip != None:
                # otherwise use existing perspective matrix...
                glLoadIdentity()
                # fov (degrees), aspect, near clip, far clip
                gluPerspective(1.0, 1.0, request.nearClip, request.farClip)
            
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            rotate = -(request.direction.rotation())
            translate = -request.start
            glRotate(math.degrees(rotate.x), 0, 0, 1)
            glRotate(math.degrees(rotate.y), 1, 0, 0)
            glRotate(math.degrees(rotate.z) + 180.0, 0, 1, 0)
            glTranslate(translate.y, translate.z, translate.x)
            
            self.drawRayCollision()
            
            glFlush()
            glFinish()
            windowWidth = self.instance.windowWidth()
            windowHeight = self.instance.windowHeight()
            
            mode = request.mode
            
            if mode == RayCollisionRequest.GET_FACE \
                    or mode == RayCollisionRequest.GET_FACE_DEPTH:
                pixels = glReadPixels(windowWidth/2, windowHeight/2, 1, 1,
                                      GL_RGB, GL_UNSIGNED_BYTE)
                color = (pixels[0], pixels[1], pixels[2])
                meshIndex, faceIndex = self.colorToFaceIndex(color)
                mesh = None
                face = None
                if meshIndex != -1:
                    mesh = self.world.rayCollisionMeshes[meshIndex]
                    face = mesh.getMesh().getFaces()[faceIndex]
                
            if mode == RayCollisionRequest.GET_DEPTH \
                    or mode == RayCollisionRequest.GET_FACE_DEPTH:
                # TODO: calculate depth
                depth = 0
                
            # callbacks
            if mode == RayCollisionRequest.GET_FACE:
                request.callback(mesh, face)
            elif mode == RayCollisionRequest.GET_DEPTH:
                request.callback(depth)
            elif mode == RayCollisionRequest.GET_FACE_DEPTH:
                request.callback(mesh, face, depth)
            
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
            
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # end for each ray collision request
        
        
        # Draw visible things
        
        glPushMatrix()
        rotate = -self.world.camera.getRotation()
        translate = -self.world.camera.getPosition()
        glRotate(math.degrees(rotate.x), 0, 0, 1)
        glRotate(math.degrees(rotate.y), 1, 0, 0)
        glRotate(math.degrees(rotate.z) + 180.0, 0, 1, 0)
        glTranslate(translate.y, translate.z, translate.x)
    
        for renderMesh in self.world.renderMeshes:
            if not renderMesh.isVisible():
                continue
            
            glPushMatrix()
            self.transformEntity(renderMesh)
            
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

        glPopMatrix()
    
    
    def drawRayCollision(self):
        i = 0
        for rayCollisionMesh in self.world.rayCollisionMeshes:
            if not rayCollisionMesh.isEnabled():
                continue
            
            glPushMatrix()
            self.transformEntity(rayCollisionMesh)
            
            j = 0
            for f in rayCollisionMesh.getMesh().getFaces():
                
                color = self.faceIndexToColor(i, j)
                glColor(color[0], color[1], color[2])
                
                glBegin(GL_POLYGON)
                for v in f.getVertices():
                    pos = v.vertex.getPosition()
                    glVertex(pos.y, pos.z, pos.x)
                glEnd()
                j += 1
            
            glPopMatrix()
            i += 1
        
    def transformEntity(self, entity):
        translate = entity.getPosition()
        rotate = entity.getRotation()
        glTranslate(translate.y, translate.z, translate.x)
        glRotate(math.degrees(rotate.z), 0, 1, 0)
        glRotate(math.degrees(rotate.y), -1, 0, 0)
        glRotate(math.degrees(rotate.x), 0, 0, 1)

    def faceIndexToColor(self, objectIndex, subIndex):
        objectIndex = int(objectIndex) + 1
        r = int(subIndex) % 256
        g = objectIndex % 256
        b = int(objectIndex / 256) % 256
        return (float(r)/256.0, float(g)/256.0, float(b)/256.0)

    # returns a tuple of (rayCollisionMeshIndex, faceIndex)
    # renderMeshIndex is -1 for nothing selected
    def colorToFaceIndex(self, color):
        r = int(color[0])
        g = int(color[1])
        b = int(color[2])
        return b*256 + g - 1, r

