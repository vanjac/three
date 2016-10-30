__author__ = "jacobvanthoog"

from threelib.files import editorStateConverter

@ editorStateConverter(-1, 0)
def convert__1_0_to_0_0(state):
    state.MAJOR_VERSION = 0
    return state

