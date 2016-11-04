__author__ = "jacobvanthoog"

import math
import threelib.sim.base

class Light(threelib.sim.base.Entity):

    def __init__(self):
        super().__init__()
        self.enabled = True
        self.ambient = (0.0, 0.0, 0.0)
        self.diffuse = (1.0, 1.0, 1.0)
        self.specular = (1.0, 1.0, 1.0)
    
    def isEnabled(self):
        return self.enabled
        
    def setEnabled(self, enabled):
        def do(toUpdateList):
            self.enabled = enabled
        self.actions.addAction(do)
        
    def getAmbient(self):
        return self.ambient
        
    def setAmbient(self, color):
        def do(toUpdateList):
            self.ambient = color
        self.actions.addAction(do)
    
    def getDiffuse(self):
        return self.diffuse
        
    def setDiffuse(self, color):
        def do(toUpdateList):
            self.diffuse = color
        self.actions.addAction(do)
    
    def getSpecular(self):
        return self.specular
        
    def setSpecular(self, color):
        def do(toUpdateList):
            self.specular = color
        self.actions.addAction(do)


class PositionalLight(Light):

    def __init__(self):
        super().__init__()
        self.attenuation = (1.0, 0.0, 0.0) # constant, linear quadratic
    
    def getAttenuation(self):
        return self.attenuation
        
    def setAttenuation(self, constant, linear, quadratic):
        def do(toUpdateList):
            self.attenuation = constant, linear, quadratic
        self.actions.addAction(do)


class SpotLight(PositionalLight):

    def __init__(self):
        super().__init__()
        self.exponent = 0.0
        self.cutoff = math.pi / 4.0

    def getExponent(self):
        return self.exponent
        
    def setExponent(self, exponent):
        def do(toUpdateList):
            self.exponent = exponent
        self.actions.addAction(do)
    
    def getCutoff(self):
        return self.cutoff
        
    def setCutoff(self, cutoff):
        def do(toUpdateList):
            self.cutoff = cutoff
        self.actions.addAction(do)

