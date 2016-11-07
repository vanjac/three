__author__ = "jacobvanthoog"

from threelib.files import editorStateConverter

@ editorStateConverter(-1, 0)
def convert__1_0_to_0_0(state):
    state.MAJOR_VERSION = 0
    return state

@ editorStateConverter(0, 0)
def convert_0_0_to_1_0(state):
    state.world.directionalLights = [ ]
    state.world.positionalLights = [ ]
    state.world.spotLights = [ ]

    state.MAJOR_VERSION = 1
    state.MINOR_VERSION = 0
    return state
