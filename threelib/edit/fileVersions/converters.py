__author__ = "jacobvanthoog"

from threelib.files import editorStateConverter

@editorStateConverter(-1, 0)
def convert__1_0_to_0_0(state):
    state.MAJOR_VERSION = 0
    return state

@editorStateConverter(0, 0)
def convert_0_0_to_1_0(state):
    state.world.directionalLights = [ ]
    state.world.positionalLights = [ ]
    state.world.spotLights = [ ]

    state.MAJOR_VERSION = 1
    state.MINOR_VERSION = 0
    return state

@editorStateConverter(1, 0)
def convert_1_0_to_1_1(state):
    for o in state.objects:
        if o.getMesh() is not None:
            mesh = o.getMesh()
            for face in mesh.getFaces():
                face.normal = None
                face.normalUpdated = False

    state.MAJOR_VERSION = 1
    state.MINOR_VERSION = 1
    return state

@editorStateConverter(1, 1)
def convert_1_1_to_1_2(state):
    state.world.renderMeshSubdivideSize = 144

    state.MAJOR_VERSION = 1
    state.MINOR_VERSION = 2
    return state

@editorStateConverter(1, 2)
def convert_1_2_to_1_3(state):
    state.MAJOR_VERSION = 1
    state.MINOR_VERSION = 3
    # "self" variable was added for action scripts
    # "math" module was added for scripts
    return state

@editorStateConverter(1, 3)
def convert_1_3_to_1_4(state):
    state.world.skyCamera = None
    state.world.skyRenderMeshes = [ ]

    state.MAJOR_VERSION = 1
    state.MINOR_VERSION = 4
    return state

@editorStateConverter(1, 4)
def convert_1_4_to_1_5(state):
    state.world.overlayCamera = None
    state.world.overlayRenderMeshes = [ ]

    state.MAJOR_VERSION = 1
    state.MINOR_VERSION = 5
    return state

@editorStateConverter(1, 5)
def convert_1_5_to_1_6(state):
    state.world.audioStream = None

    state.MAJOR_VERSION = 1
    state.MINOR_VERSION = 6
    return state

@editorStateConverter(1, 6)
def convert_1_6_to_1_7(state):
    for o in state.objects:
        o.templateName = ""

    state.MAJOR_VERSION = 1
    state.MINOR_VERSION = 7
    return state

@editorStateConverter(1, 7)
def convert_1_7_to_1_8(state):
    from threelib.vectorMath import Vector

    for o in state.objects:
        if o.getMesh() is not None:
            for face in o.getMesh().getFaces():
                face.textureScale *= Vector(1, -1, 1)
                face.calculateTextureVertices()

    state.MAJOR_VERSION = 1
    state.MINOR_VERSION = 8
    return state

@editorStateConverter(1, 8)
def convert_1_8_to_1_9(state):
    from threelib.edit.objects import SolidMeshObject

    for o in state.objects:
        if isinstance(o, SolidMeshObject):
            o.staticVisibleMesh = True

    state.MAJOR_VERSION = 1
    state.MINOR_VERSION = 9
    return state
