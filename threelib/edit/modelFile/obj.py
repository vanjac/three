__author__ = "jacobvanthoog"

from threelib.mesh import *

def loadOBJ(path):
    print("Load OBJ", path)
    with path.open() as f:
        text = f.read()
    lines = text.splitlines()

    mesh = Mesh()

    for line in lines:
        line = line.strip()
        if line == "":
            continue
        words = line.split()
        command = words[0]

        if command == '#':
            # comment
            continue
        elif command == 'usemtl':
            # material set
            pass # TODO
        elif command == 'v':
            # vertex
            pass # TODO
        elif command == 'vt':
            # texture vertex
            pass # TODO
        elif command == 'vn':
            # vertex normal
            pass # TODO
        elif command == 'f':
            # face
            pass # TODO

    if mesh.isEmpty():
        print("No data in OBJ file!")
        return None
    else:
        return mesh

