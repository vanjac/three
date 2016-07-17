__author__ = "vantjac"

class World:
    
    def __init__(self):
        self.materials = [ ] # list of MaterialReference's

    def addMaterial(self, materialReference):
        self.materials.append(materialReference)

    def removeMaterialReference(self, material):
        material.removeReference()
        
        if material.hasNoReferences:
            self.materials.remove(material)
            print("Removing unused material", material.getName())

    def findMaterial(self, name):
        for matRef in self.materials:
            if matRef.getName() == name:
                return matRef

        return None
