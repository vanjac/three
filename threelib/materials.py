__author__ = "vantjac"

from threelib import files
from array import array
import struct

class Material:
    
    def __init__(self):
        self.texture = None
        self.isTransparent = False
        self.xLen = 0
        self.yLen = 0

    # prevent pickling:
    # see https://docs.python.org/3/library/pickle.html#object.__getstate__

    def __getstate__():
        return None
    def __setstate__(state):
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
        # based on opengl-tutorial.org/beginners-tutorials/tutorial-5-a-textured-cube
        materialPath = files.getMaterial(name)
        with materialPath.open('rb') as f:
            fBytes = f.read()
            # read the header...
            if fBytes[0] != b'B'[0] or fBytes[1] != b'M'[0]:
                print("Not a valid BMP file!")
                return
            dataPos = struct.unpack('<I', fBytes[10:14])[0]
            bitsPerPixel = struct.unpack('<H', fBytes[28:30])[0]

            if bitsPerPixel != 24 and bitsPerPixel != 32:
                print("Unrecognized bits per pixel")
                return
            self.xLen = struct.unpack('<I', fBytes[18:22])[0]
            self.yLen = struct.unpack('<I', fBytes[22:26])[0]
            if dataPos == 0:
                dataPos = 54
            
            print("Image size: " + str(self.xLen) + ", " + str(self.yLen))
            print("Bits per pixel: " + str(bitsPerPixel))

            self.texture = array('B')
            index = dataPos
            for i in range(0, self.xLen * self.yLen):
               self.texture.append(fBytes[index+2]) #R
               self.texture.append(fBytes[index+1]) #G
               self.texture.append(fBytes[index+0]) #B
               if bitsPerPixel == 32:
                   self.texture.append(fBytes[index+3])
               else:
                   self.texture.append(255)
                   index += int(bitsPerPixel / 8)

class MaterialReference:
    
    def __init__(self, name, addReference=False, load=False):
        self.name = name
        self.material = Material()
        self.references = 1 if addReference else 0
        if load:
            self.load()

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
