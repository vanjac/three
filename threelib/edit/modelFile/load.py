__author__ = "jacobvanthoog"

from threelib.edit.modelFile.obj import loadOBJ

def loadModel(path):
    """
    Return a mesh.
    """
    extension = path.suffix
    if extension == '.obj':
        return loadOBJ(path)
    return None

