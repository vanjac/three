__author__ = "jacobvanthoog"

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
    """
    A texture image
    """
    def __init__(self, data, dataType, xLen, yLen):
        self.data = data
        self.dataType = dataType
        self.xLen = xLen
        self.yLen = yLen

    def getData(self):
        """
        An array of chars, of size xLen * yLen * numChannels.
        """
        return self.data

    def getXLen(self):
        """
        Return the width of the image in pixels.
        """
        return self.xLen

    def getYLen(self):
        """
        Return the height of the image in pixels.
        """
        return self.yLen

    def getDataType(self):
        """
        The data type of the image, as a string. Values correspond with PIL
        image modes (like "RGB" or "RGBA").
        """
        return self.dataType


class MaterialReference(Resource):
    """
    A material that can be painted onto a mesh face.
    """

    def __init__(self, name):
        """
        Create a material with the specified name. The name is a path relative
        to the materials directory, without a file extension.
        """
        super().__init__()
        self.name = name
        self.number = 0
        self.loaded = False
        self.aspectRatio = 1.0

    def getName(self):
        """
        Get the name of the material. The name is a path relative to the
        materials directory, without a file extension.
        """
        return self.name

    def getNumber(self):
        """
        Return the number stored with ``setNumber``.
        """
        return self.number

    def setNumber(self, number):
        """
        Set an ID number to be associated with this material. This is intended
        to be used by 3d rendering; for example, for OpenGL this could store the
        texture object's "name."
        """
        self.number = number

    def isLoaded(self):
        """
        Check if the material loaded flag was set by ``setLoaded``.
        """
        return self.loaded

    def setLoaded(self, loaded=True):
        """
        Set a flag for whether the texture has been loaded. For 3d rendering.
        """
        self.loaded = loaded

    def getAspectRatio(self):
        """
        Get the aspect ratio of the texture, as a ratio of the width to the
        height.
        """
        return self.aspectRatio

    def hasAlbedoTexture(self):
        # TODO: what is this used for?
        return self.hasTexture

    def loadAlbedoTexture(self):
        """
        Load the albedo texture for this material, and return a Texture object.
        The albedo is the base color of the material.
        """
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

        # dimensions need to be a power of 2
        if not (isPowerOf2(xLen) and isPowerOf2(yLen)):
            print("Scaling from", str(xLen) + ", " + str(yLen), end=' ')
            # search upwards for the next power of 2
            xLen = 2 ** math.ceil(math.log(xLen, 2))
            yLen = 2 ** math.ceil(math.log(yLen, 2))
            print("to", str(xLen) + ", " + str(yLen))

            image = image.resize((xLen, yLen), Image.BICUBIC)
        else:
            print("Size is", str(xLen) + ", " + str(yLen))

        texture = list(image.tobytes())
        self.hasTexture = True
        self.aspectRatio = float(xLen) / float(yLen)
        return Texture(texture, image.mode, xLen, yLen)

