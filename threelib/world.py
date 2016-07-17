__author__ = "vantjac"

class World:
    
    def __init__(self):
        self.materials = [ ] # list of MaterialReference's

    def removeMaterialReference(self, material):
        material.removeReference()
        if material.hasNoReferences:
            self.materials.remove(material)
