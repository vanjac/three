__author__ = "jacobvanthoog"

from threelib.run.appInterface.gameInterface import GameInterface
from threelib.world import RayCollisionRequest
from threelib.sim.lighting import *
from threelib.vectorMath import Vector
from threelib.vectorMath import Rotate

import math

import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class GLRunner(GameInterface):

    MAX_LIGHTS = 8

    def __init__(self, state=None):
        super().__init__(state)
        print("OpenGL 1 Game Runner")
        self.lightingEnabled = False

    def init(self):
        super().init()

        glPixelStorei(GL_UNPACK_ALIGNMENT, 1) # for getting select pixels
                                             # and storing textures
        # must be GL_MODULATE for lighting to work with textures:
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialfv(GL_FRONT, GL_SHININESS, [50.0])
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.0, 0.0, 0.0, 0.0])

        lightIndex = 0
        for light in self.world.directionalLights \
                   + self.world.positionalLights \
                   + self.world.spotLights:
            if lightIndex >= GLRunner.MAX_LIGHTS:
                print("Too many lights! (" + str(GLRunner.MAX_LIGHTS) +
                      " maximum). Additional lights will be skipped.")
                break
            light.setNumber(lightIndex)
            lightIndex += 1
        print(str(lightIndex) + " lights")
        self.lightingEnabled = lightIndex != 0

        self.instance.updateMaterials(self.world)

    def draw(self):
        super().draw()

        # clear screen and depth buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Ray collisions
        while self.world.hasRayCollisionRequest():
            request = self.world.nextRayCollisionRequest()

            nearClip = request.nearClip
            if nearClip is None:
                nearClip = self.instance.getNearClip()
            farClip = request.farClip
            if farClip is None:
                farClip = self.instance.getFarClip()

            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            # fov (degrees), aspect, near clip, far clip
            gluPerspective(1.0, 1.0, nearClip, farClip)

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
                pixels = glReadPixels(windowWidth/2, windowHeight/2, 1, 1,
                                      GL_DEPTH_COMPONENT, GL_FLOAT)
                depthComponent = pixels[0][0]
                if depthComponent == 1:
                    depth = None
                else:
                    # https://www.opengl.org/discussion_boards/showthread.php/171104-Convert-value-from-Z-buffer-to-Z-coordinate
                    projectionMatrix = glGetDoublev(GL_PROJECTION_MATRIX)
                    depth = projectionMatrix[3][2] / ( depthComponent * -2.0
                        + 1.0 - projectionMatrix[2][2] ) * -1

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


        # Translate camera

        glPushMatrix()
        rotate = -self.world.camera.getRotation()
        translate = -self.world.camera.getPosition()
        glRotate(math.degrees(rotate.x), 0, 0, 1)
        glRotate(math.degrees(rotate.y), 1, 0, 0)
        glRotate(math.degrees(rotate.z) + 180.0, 0, 1, 0)
        glTranslate(translate.y, translate.z, translate.x)

        if self.lightingEnabled:
            glEnable(GL_LIGHTING)

        self.updateLights()

        # Draw RenderMeshes

        self.drawRenderMeshes(self.world.renderMeshes)

        glPopMatrix()

        if self.lightingEnabled:
            glDisable(GL_LIGHTING)

        # Frame rate text
        self.instance.drawText(str(self.instance.getFps()) + " FPS",
                               GLUT_BITMAP_9_BY_15,
                               4, self.instance.windowHeight() - 19) # 4+15


    def drawRenderMeshes(self, renderMeshes):
        currentMat = None
        glDisable(GL_TEXTURE_2D)
        glColor(0.8, 0.8, 0.8)
        for renderMesh in renderMeshes:
            if not renderMesh.isVisible():
                continue

            glPushMatrix()
            self.transformEntity(renderMesh)

            for f in renderMesh.getMesh().getFaces():
                faceMat = f.getMaterial()
                if faceMat is not currentMat:
                    if faceMat is None or not faceMat.isLoaded():
                        glDisable(GL_TEXTURE_2D)
                    else:
                        glEnable(GL_TEXTURE_2D)
                        glBindTexture(GL_TEXTURE_2D, faceMat.getNumber())
                    currentMat = faceMat

                normal = f.getNormal()
                glNormal(normal.y, normal.z, normal.x)
                glBegin(GL_POLYGON)
                for v in f.getVertices():
                    pos = v.vertex.getPosition()
                    texPos = v.textureVertex
                    glTexCoord(texPos.x, texPos.y)
                    glVertex(pos.y, pos.z, pos.x)
                glEnd()

            glPopMatrix()
        glDisable(GL_TEXTURE_2D)


    def updateLights(self):
        for light in self.world.directionalLights:
            glLight = self.getGLLightConstant(light.getNumber())
            if not light.isEnabled():
                if light.hasChanged():
                    glDisable(glLight)
                continue
            if light.hasChanged():
                self.updateGenericLightParameters(light, glLight)

            direction = -(Vector(1, 0, 0).rotate(light.getRotation()))
            glLightfv(glLight, GL_POSITION,
                      [direction.y, direction.z, direction.x, 0.0])

        for light in self.world.positionalLights:
            glLight = self.getGLLightConstant(light.getNumber())
            if not light.isEnabled():
                if light.hasChanged():
                    glDisable(glLight)
                continue
            if light.hasChanged():
                self.updateGenericLightParameters(light, glLight)
                self.updatePositionalLightParameters(light, glLight)

            self.updatePositionalLightPosition(light, glLight)

        for light in self.world.spotLights:
            glLight = self.getGLLightConstant(light.getNumber())
            if not light.isEnabled():
                if light.hasChanged():
                    glDisable(glLight)
                continue
            if light.hasChanged():
                self.updateGenericLightParameters(light, glLight)
                self.updatePositionalLightParameters(light, glLight)

            self.updatePositionalLightPosition(light, glLight)
            direction = Vector(1, 0, 0).rotate(light.getRotation())
            glLightfv(glLight, GL_SPOT_DIRECTION,
                      [direction.y, direction.z, direction.x])
            glLightf(glLight, GL_SPOT_EXPONENT, light.getExponent())
            glLightf(glLight, GL_SPOT_CUTOFF, math.degrees(light.getCutoff()))

    def updateGenericLightParameters(self, light, glLight):
        glEnable(glLight)
        glLightfv(glLight, GL_AMBIENT, light.getAmbient())
        glLightfv(glLight, GL_DIFFUSE, light.getDiffuse())
        glLightfv(glLight, GL_SPECULAR, light.getSpecular())

    def updatePositionalLightParameters(self, light, glLight):
        attenuation = light.getAttenuation()
        glLightf(glLight, GL_CONSTANT_ATTENUATION, attenuation[0])
        glLightf(glLight, GL_LINEAR_ATTENUATION, attenuation[1])
        glLightf(glLight, GL_QUADRATIC_ATTENUATION, attenuation[2])

    def updatePositionalLightPosition(self, light, glLight):
        pos = light.getPosition()
        glLightfv(glLight, GL_POSITION, [pos.y, pos.z, pos.x, 1.0])

    def getGLLightConstant(self, number):
        if number > GLRunner.MAX_LIGHTS:
            return None
        else:
            return [GL_LIGHT0, GL_LIGHT1, GL_LIGHT2, GL_LIGHT3, \
                    GL_LIGHT4, GL_LIGHT5, GL_LIGHT6, GL_LIGHT7] [number]

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

