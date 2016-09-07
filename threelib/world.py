__author__ = "vantjac"

class World:
    
    def __init__(self):
        self.materials = [ ] # list of MaterialReference's
        self.addedMaterials = [ ]
        self.removedMaterials = [ ]
        self.updatedMaterials = [ ]

    def onLoad(self):
        for mat in self.materials:
            self.addedMaterials.append(mat)
            mat.setLoaded(False)

    def addMaterial(self, materialReference):
        self.materials.append(materialReference)
        self.addedMaterials.append(materialReference)

    def removeMaterialReference(self, material):
        material.removeReference()
        
        if material.hasNoReferences():
            self.removeMaterial(material)
            print("Removing unused material", material.getName())
            
    def removeMaterial(self, material):
        self.materials.remove(material)
        self.removedMaterials.append(material)

    def updateMaterial(self, materialReference):
        self.updatedMaterials.append(materialReference)

    def removeUnusedMaterials(self):
        materialsToRemove = [ ]
        for material in self.materials:
            if material.hasNoReferences():
                materialsToRemove.append(material)
        for material in materialsToRemove:
            self.removeMaterial(material)
            print("Removing unused material", material.getName())

    # materials that have been added or removed since last check
    
    def getAddedMaterials(self):
        added = self.addedMaterials
        self.addedMaterials = [ ]
        return added

    def getUpdatedMaterials(self):
        updated = self.updatedMaterials
        self.updatedMaterials = [ ]
        return updated

    def getRemovedMaterials(self):
        removed = self.removedMaterials
        self.removedMaterials = [ ]
        return removed

    def findMaterial(self, name):
        for matRef in self.materials:
            if matRef.getName() == name:
                return matRef

        return None


class Resource:
    
    def __init__(self):
        self.references = 0

    def numReferences(self):
        return self.references

    def addReference(self):
        self.references += 1

    def removeReference(self):
        self.references -= 1

    def hasNoReferences(self):
        return self.references == 0
