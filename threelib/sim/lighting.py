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
        self.number = None
        self.changed = True
        
    def getNumber(self):
        """
        Return the number stored with ``setNumber``.
        """
        return self.number

    def setNumber(self, number):
        """
        Set an ID number to be associated with this light. This is intended
        to be used by 3d rendering, to identify the light.
        """
        self.number = number
        
    def hasChanged(self):
        """
        Check if any visible properties about this light have changed since
        the last call to ``hasChanged``. Always returns True the first time.
        """
        flag = self.changed
        self.changed = False
        return flag
    
    def isEnabled(self):
        return self.enabled
        
    def setEnabled(self, enabled):
        def do(toUpdateList):
            self.enabled = enabled
            self.changed = True
        self.actions.addAction(do)
        
    def getAmbient(self):
        return self.ambient
        
    def setAmbient(self, color):
        def do(toUpdateList):
            self.ambient = color
            self.changed = True
        self.actions.addAction(do)
    
    def getDiffuse(self):
        return self.diffuse
        
    def setDiffuse(self, color):
        def do(toUpdateList):
            self.diffuse = color
            self.changed = True
        self.actions.addAction(do)
    
    def getSpecular(self):
        return self.specular
        
    def setSpecular(self, color):
        def do(toUpdateList):
            self.specular = color
            self.changed = True
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
            self.changed = True
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
            self.changed = True
        self.actions.addAction(do)
    
    def getCutoff(self):
        return self.cutoff
        
    def setCutoff(self, cutoff):
        def do(toUpdateList):
            self.cutoff = cutoff
            self.changed = True
        self.actions.addAction(do)

