__author__ = "vantjac"

from threelib import files
from array import array
import struct
import math

# for texture scaling
from PIL import Image

def isPowerOf2(num):
    # from:
    # code.activestate.com/recipes/577514-chek-if-a-number-is-a-power-of-two/
    return num != 0 and ((num & (num - 1)) == 0)

class Material:
    
    def __init__(self):
        self.texture = [ ]
        self.isTransparent = False
        self.xLen = 0
        self.yLen = 0

    # prevent pickling:
    # see https://docs.python.org/3/library/pickle.html#object.__getstate__

    def __getstate__(self):
        return None
    def __setstate__(self, state):
        pass
    

    def isTransparent(self):
        return self.isTransparent
    
    # an array of chars, of size xLen * yLen * 4
    # ordered RGBA
    def getTexture(self):
        return self.texture

    def getPixel(self, x, y):
        index = (x + y * self.xLen) * 4;
        return(self.texture[index+0], self.texture[index+1],
               self.texture[index+2], self.texture[index+3])

    def getXLen(self):
        return self.xLen

    def getYLen(self):
        return self.yLen

    def load(self, name):
        materialPath = files.getMaterial(name)
        if materialPath == None:
            print("Material not found:", name)
            return
        
        print("Reading image at", materialPath)
        image = Image.open(materialPath)
        image.load()
        image = image.convert('RGBA')
        self.xLen = image.width
        self.yLen = image.height

        print("Size is", str(self.xLen) + ", " + str(self.yLen))
            
        # dimensions need to be a power of 2
        if not (isPowerOf2(self.xLen) and isPowerOf2(self.yLen)):
            # search upwards for the next power of 2
            self.xLen = 2 ** math.ceil(math.log(self.xLen, 2))
            self.yLen = 2 ** math.ceil(math.log(self.yLen, 2))
            print("Scaling up to", str(self.xLen) + ", " + str(self.yLen))
            
            image = image.resize((self.xLen, self.yLen), Image.BICUBIC)
        
        self.texture = list(image.tobytes())

        print("Done loading image")


class MaterialReference:
    
    def __init__(self, name, load=False):
        self.name = name
        self.number = 0
        self.material = Material()
        self.references = 0
        if load:
            self.load()

    def getName(self):
        return self.name

    # used by 3d rendering
    # for example, for OpenGL this is the texture object's "name"
    
    def getNumber(self):
        return self.number

    def setNumber(self, number):
        self.number = number

    def load(self):
        self.material.load(self.name)

    def numReferences(self):
        return self.references

    def addReference(self):
        self.references += 1

    def removeReference(self):
        self.references -= 1

    def hasNoReferences(self):
        return self.references == 0
