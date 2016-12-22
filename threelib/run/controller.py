__author__ = "jacobvanthoog"

import threelib.script

class GameController:

    def __init__(self):
        threelib.script.setVariableValue("controller", self)

    def setState(self, state):
        pass

    def getRunner(self):
        pass
