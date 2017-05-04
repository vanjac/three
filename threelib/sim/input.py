__author__ = "jacobvanthoog"

import numbers

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

    def __neg__(self):
        return AxisOpposite(self)

    def __add__(self, other):
        if isinstance(other, numbers.Number):
            return AxisOffset(self, other)
        else:
            return AxisSum(self, other)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, numbers.Number):
            return AxisOffset(self, -other)
        else:
            return AxisSum(self, -other)

    def __rsub__(self, other):
        if isinstance(other, numbers.Number):
            return AxisOffset(-self, other)
        else:
            return AxisSum(-self, other)

    def __mul__(self, other):
        if isinstance(other, numbers.Number):
            return AxisScale(self, other)
        else:
            return AxisProduct(self, other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, numbers.Number):
            return AxisScale(self, 1.0 / other)
        else:
            return AxisProduct(self, AxisReciprocal(other))

    def __rtruediv__(self, other):
        if isinstance(other, numbers.Number):
            return AxisScale(AxisReciprocal(self), other)
        else:
            return AxisProduct(AxisReciprocal(self), other)


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
        self.value = 0.0
        super().__init__()

    def getValue(self):
        return self.value

    def setValue(self, value):
        self.value = float(value)

    def changeValue(self, amount):
        self.value += amount


class ButtonAxis(AxisInput):

    def __init__(self, button, offValue=0.0, onValue=1.0):
        self.button = button
        self.offValue = float(offValue)
        self.onValue = float(onValue)
        super().__init__()

    def getValue(self):
        return self.onValue if self.button.isPressed() else self.offValue

class AxisOffset(AxisInput):

    def __init__(self, axis, offset):
        self.axis = axis
        self.offset = float(offset)
        super().__init__()

    def getValue(self):
        return self.axis.getValue() + self.offset

class AxisScale(AxisInput):

    def __init__(self, axis, scale):
        self.axis = axis
        self.scale = float(scale)
        super().__init__()

    def getValue(self):
        return self.axis.getValue() * self.scale

class AxisOpposite(AxisInput):

    def __init__(self, axis):
        self.axis = axis
        super().__init__()

    def getValue(self):
        return -float(self.axis.getValue())

class AxisReciprocal(AxisInput):

    def __init__(self, axis):
        self.axis = axis
        super().__init__()

    def getValue(self):
        return 1.0 / self.axis.getValue()

class AxisSum(AxisInput):

    def __init__(self, axis1, axis2):
        self.axis1 = axis1
        self.axis2 = axis2
        super().__init__()

    def getValue(self):
        return float(self.axis1.getValue()) + float(self.axis2.getValue())

class AxisProduct(AxisInput):

    def __init__(self, axis1, axis2):
        self.axis1 = axis1
        self.axis2 = axis2
        super().__init__()

    def getValue(self):
        return float(self.axis1.getValue()) * float(self.axis2.getValue())

