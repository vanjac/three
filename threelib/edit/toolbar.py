__author__ = "jacobvanthoog"


class Style:

    def __init__(self, background, foreground=(255,255,255)):
        self.background = background
        self.foreground = foreground


class Button:

    def __init__(self, text="", x=0.0, width=1.0, style=Style((127,127,127)),
                 keyboardShortcut=None):
        self.mousePressedAction = None # function()
        self.mouseDraggedAction = None # function(x, y)
        self.mouseReleasedAction = None # function()
        # if None, same as mousePressedAction:
        self.keyboardAction = None # boolean function(command)

        self.keyboardShortcut = keyboardShortcut

        self.x = x
        self.width = width

        self.text = text

        self.style = style


class Row:

    def __init__(self, height=32):
        self.height = height
        self.buttons = [ ]

    def addButton(self, button):
        self.buttons.append(button)


class Group:

    def __init__(self, name=""):
        self.name = name
        self.shown = False
        self.rows = [ ]

    def addRow(self, row):
        self.rows.append(row)
