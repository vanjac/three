__author__ = "vantjac"

from threelib import files
from array import array
import struct
import math
from threelib.world import Resource

# for texture scaling
from PIL import Image

def isPowerOf2(num):
    # from:
    # code.activestate.com/recipes/577514-chek-if-a-number-is-a-power-of-two/
    return num != 0 and ((num & (num - 1)) == 0)

class Texture:
    
    def __init__(self, data, dataType, xLen, yLen):
        self.data = data
        self.dataType = dataType
        self.xLen = xLen
        self.yLen = yLen
    
    # for RGBA mode:
    # an array of chars, of size xLen * yLen * 4, ordered RGBA
    def getData(self):
        return self.data

    def getXLen(self):
        return self.xLen

    def getYLen(self):
        return self.yLen

    def getDataType(self):
        return self.dataType


class MaterialReference(Resource):
    
    def __init__(self, name, load=False):
        super().__init__()
        self.name = name
        self.number = 0
        self.loaded = False
        self.aspectRatio = 1.0

    def getName(self):
        return self.name

    # used by 3d rendering
    # for example, for OpenGL this is the texture object's "name"
    
    def getNumber(self):
        return self.number

    def setNumber(self, number):
        self.number = number

    # used by 3d rendering
    # flag to determine if texture has been loaded
    def isLoaded(self):
        return self.loaded

    def setLoaded(self, loaded=True):
        self.loaded = loaded

    def getAspectRatio(self):
        return self.aspectRatio

    def hasAlbedoTexture(self):
        return self.hasTexture

    def loadAlbedoTexture(self):
        materialPath = files.getMaterial(self.name)
        if materialPath == None:
            print("Material not found:", self.name)
            return None
        
        print("Reading image at", materialPath)
        image = Image.open(materialPath)
        image.load()
        if image.mode != 'RGB' and image.mode != 'RGBA':
            image = image.convert('RGB')
        xLen = image.width
        yLen = image.height

        print("Size is", str(xLen) + ", " + str(yLen))
            
        # dimensions need to be a power of 2
        if not (isPowerOf2(xLen) and isPowerOf2(yLen)):
            # search upwards for the next power of 2
            xLen = 2 ** math.ceil(math.log(xLen, 2))
            yLen = 2 ** math.ceil(math.log(yLen, 2))
            print("Scaling up to", str(xLen) + ", " + str(yLen))
            
            image = image.resize((xLen, yLen), Image.BICUBIC)
        
        texture = list(image.tobytes())

        print("Done loading image")
        self.hasTexture = True
        self.aspectRatio = float(xLen) / float(yLen)
        return Texture(texture, image.mode, xLen, yLen)
