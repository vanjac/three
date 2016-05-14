__author__ = "vantjac"

from vectorMath import *

class Entity:
    
    def __init__(self, position = ZERO_V, rotation = ZERO_R):
        self.position = position
        self.rotation = rotation
        self.parent = None
        self.children = [ ]

    def getPosition(self):
        return self.position

    def getRotation(self):
        return self.rotation
        
    def move(self, translate, rotate):
        self.position = self.position + translate
        self.rotation = self.rotation + rotate

    def getParent(self):
        return self.parent

    def setParent(self, parent):
        self.parent = parent
    
    def getChildren(self):
        return self.children

    def addChild(self, child):
        self.children.append(child)

    def removeChild(self, child):
        self.children.remove(child)

    def update(self, time):
        pass

    def readyToDelete():
        return False
