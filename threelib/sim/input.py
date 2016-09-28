__author__ = "jacobvanthoog"

class ButtonInput:

    NO_EVENT = "none"
    PRESSED_EVENT = "pressed"
    RELEASED_EVENT = "released"

    def __init__(self):
        self._lastPressed = self.isPressed()
        
    def isPressed(self):
        """
        Check if the button is pressed. Override this!
        """
        return False
        
    def getEvent(self):
        """
        Check if the button was pressed or released since the last time this
        method was called. Return ``ButtonInput.NO_EVENT``,
        ``ButtonInput.PRESSED_EVENT``, or ``ButtonInput.RELEASED_EVENT``
        """
        pressed = self.isPressed()
        
        if pressed == self._lastPressed:
            event = ButtonInput.NO_EVENT
        elif pressed and (not self._lastPressed):
            event = ButtonInput.PRESSED_EVENT
        elif (not pressed) and self._lastPressed:
            event = ButtonInput.RELEASED_EVENT
        
        self._lastPressed = pressed
        return event        

class AxisInput:

    def __init__(self):
        self._lastValue = self.getValue()

    def getValue(self):
        """
        Get the value of the axis as a float. Override this!
        """
        return 0.0
        
    def getChange(self):
        """
        Get the amount the axis value has changed since the last time this
        method was called.
        """
        newValue = self.getValue()
        change = newValue - self._lastValue
        self._lastValue = newValue
        return change


class SimpleButtonInput(ButtonInput):

    def __init__(self):
        self.pressed = False
        super().__init__()
        
    def isPressed(self):
        return self.pressed
        
    def setPressed(self, pressed):
        self.pressed = pressed

class SimpleAxisInput(AxisInput):
    
    def __init__(self):
        self.value = 0
        super().__init__()

    def getValue(self):
        return self.value
        
    def setValue(self, value):
        self.value = value
        
    def changeValue(self, amount):
        self.value += amount

