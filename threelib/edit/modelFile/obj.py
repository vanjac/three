__author__ = "jacobvanthoog"

from threelib.mesh import *
from threelib.vectorMath import Vector

# TODO: smoothing groups
# TODO: normals
# TODO: prevent texture vertices from changing
# TODO: Materials

def loadOBJ(path):
    print("Load OBJ", path)
    with path.open() as f:
        text = f.read()
    lines = text.splitlines()

    mesh = Mesh()
    textureVertices = [ ]
    vertexNormals = [ ]

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
            try:
                vertexPos = Vector(
                    float(words[3]), float(words[1]), float(words[2]))
            except (ValueError, IndexError):
                print("ERROR: Invalid vertex command:", line)
                continue
            vertex = MeshVertex(vertexPos)
            mesh.addVertex(vertex)
        elif command == 'vt':
            # texture vertex
            try:
                if len(words) == 2:
                    textureVertexPos = Vector(float(words[1]), 0)
                elif len(words) == 3:
                    textureVertexPos = Vector(float(words[1]), float(words[2]))
                elif len(words) == 4:
                    textureVertexPos = Vector(
                        float(words[1]), float(words[2]), float(words[3]))
                else:
                    print("ERROR: Invalid texture vertex command:", line)
                    continue
                textureVertices.append(textureVertexPos)
            except ValueError:
                print("ERROR: Invalid texture vertex command:", line)
                continue
        elif command == 'vn':
            # vertex normal
            try:
                normal = Vector(
                    float(words[3]), float(words[1]), float(words[2]))
            except (ValueError, IndexError):
                print("ERROR: Invalid vertex normal command:", line)
                continue
            vertexNormals.append(normal)
        elif command == 'f':
            # face
            face = MeshFace()
            if len(words) < 4:
                print("ERROR: Invalid face command:", line)
                continue
            for vertexWord in words[1:]:
                values = vertexWord.split('/')
                try:
                    vertexIndex = int(values[0])
                    textureVertexIndex = 0
                    vertexNormalIndex = 0
                    if len(values) >= 2:
                        if values[1] != '':
                            textureVertexIndex = int(values[1])
                        if len(values) >= 3:
                            vertexNormalIndex = int(values[2])
                except ValueError:
                    print("ERROR: Invalid face command:", line)
                    continue
                vertex = objIndex(mesh.getVertices(), vertexIndex)
                textureVertex = objIndex(textureVertices, textureVertexIndex)
                vertexNormal = objIndex(vertexNormals, vertexNormalIndex)
                # TODO do something with the normal
                face.addVertex(vertex, textureVertex=textureVertex)
            mesh.addFace(face)

    if mesh.isEmpty():
        print("No data in OBJ file!")
        return None
    else:
        return mesh

def objIndex(l, index):
    try:
        if index > 0:
            return l[index - 1]
        elif index < 0:
            return l[index]
        else:
            return None
    except IndexError:
        return None

