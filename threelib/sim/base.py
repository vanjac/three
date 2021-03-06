__author__ = "jacobvanthoog"

from threelib.vectorMath import Vector
from threelib.vectorMath import Rotate

class SimObject:
    """
    An object in the game simulation.
    """

    def scan(self, timeElapsed, totalTime):
        """
        Based on current world state, decide what the SimObject's next actions
        will be, when update() is called.
        """
        pass

    def setSimulationSpeed(self, speed):
        """
        Speed is a time scale relative to the "real world": 1 is normal speed,
        2 is twice as fast as real time, .5 is half as fast, 0 is paused. Only
        SimObjects that interface with the real world should pay attention to
        this. Has no effect until update() is called.
        """
        pass

    def init(self):
        """
        Initialize SimObject. No effect until update().
        """
        pass

    def start(self):
        """
        Called when the SimObject starts in the World. init() should have
        already been called. No effect until update().
        """
        pass

    def end(self):
        """
        Called when the SimObject is removed from the World. No effect until
        update().
        """
        pass

    def destroy(self):
        """
        Called when the SimObject is no longer needed. No effect until update().
        """
        pass

    def update(self):
        """
        Make any updates that had been planned previously. No public properties
        of the SimObject should change until this method is called. Should
        return a list of other SimObjects that will need to be updated again, if
        they haven't already, or None.
        """
        pass

    def readyToRemove(self):
        """
        Return True if the SimObject is ready to be removed from the world.
        Should only update state when update() is called.
        """
        return False


class ActionList:
    """
    A list of actions that accumulates, until they are all run at once and the
    list is cleared.
    """

    def __init__(self):
        self.actions = [ ]

    def addAction(self, action):
        """
        ``action`` should be a function that takes a single argument: a List of
        things to update, which it may add to.
        """
        self.actions.append(action)

    def doActions(self):
        """
        Do all of the actions that have been added so far, and clear the list.
        Return the total List of things to update.
        """
        toUpdateList = [ ]
        for action in self.actions:
            action(toUpdateList)
        self.actions = [ ]
        return toUpdateList


class Simulator(SimObject):
    """
    A special SimObject that contains multiple SimObjects, which are all
    simulated at once.
    """

    def __init__(self):
        self.actions = ActionList()
        self.objects = [ ]
        self.simSpeed = 1

        self.initialized = False
        self.started = False

    def getObjects(self):
        """
        Get all simulated objects.
        """
        return self.objects

    def addObject(self, o):
        """
        Add an object to simulation. No effect until update().
        """
        def do(toUpdateList):
            self.objects.append(o)
            o.setSimulationSpeed(self.simSpeed)
            if self.initialized:
                o.init()
            if self.started:
                o.start()
        self.actions.addAction(do)

    def removeObject(self, o):
        """
        Remove an object from simulation. No effect until update().
        """
        def do(toUpdateList):
            self.objects.remove(o)
            if self.started:
                o.end()
            if self.initialized:
                o.destroy()
        self.actions.addAction(do)


    def scan(self, timeElapsed, totalTime):
        for o in self.objects:
            o.scan(timeElapsed, totalTime)

    def setSimulationSpeed(self, speed):
        self.simSpeed = speed
        for o in self.objects:
            o.setSimulationSpeed(speed)

    def init(self):
        self.initialized = True
        for o in self.objects:
            o.init()

    def start(self):
        self.started = True
        for o in self.objects:
            o.start()

    def end(self):
        self.started = False
        for o in self.objects:
            o.end()

    def destroy(self):
        self.initialized = False
        for o in self.objects:
            o.destroy()

    def update(self):
        for o in self.objects:
            if o.readyToRemove():
                self.removeObject(o)
        self.actions.doActions()

        objectsToUpdate = list(self.objects)
        while len(objectsToUpdate) != 0:
            o = objectsToUpdate.pop()
            addedObjects = o.update()
            if addedObjects is not None:
                for addedObject in addedObjects:
                    if not addedObject in objectsToUpdate:
                        objectsToUpdate.append(addedObject)


class Entity(SimObject):
    """
    A SimObject that has:
    - A position and rotation
    - A set of "children," and a reference to its parent.
    - Built in implementations for ``update()`` and ``readyToRemove()``.
    """

    def __init__(self, position=Vector(0, 0, 0), rotation=Rotate(0, 0, 0)):
        super().__init__()
        self.actions = ActionList()

        self.position = position
        self.rotation = rotation
        self.parent = None
        self.children = [ ]

        self.remove = False

    def kill(self, children=False):
        """
        Mark this Entity, and optionally its children, as ready to remove. No
        effect until update().
        """

        def do(toUpdateList):
            self.remove = True
            if children:
                for child in list(self.children):
                    child.kill(children=True)
                    toUpdateList.append(child)
        self.actions.addAction(do)

    def getPosition(self):
        return self.position

    def getRotation(self):
        return self.rotation

    def translate(self, vector, moveChildren=True):
        """
        Change the position of this Entity, and optionally its children. No
        effect until update().
        """

        def do(toUpdateList):
            self.position += vector
            if moveChildren:
                for child in list(self.children):
                    child.translate(vector, True)
                    toUpdateList.append(child)
        self.actions.addAction(do)

    def rotate(self, rotate, moveChildren=True):
        """
        Rotate this Entity, and optionally its children (they will be rotated
        around this Entity). No effect until update().
        """

        def do(toUpdateList):
            self.rotation = self.rotation.rotate(rotate)
            if moveChildren:
                for child in self.children:
                    child.rotate(rotate, True)
                    startPosition = child.getPosition()
                    endPosition = startPosition.rotateAround(rotate,
                        self.getPosition())
                    child.translate(endPosition - startPosition)
                    toUpdateList.append(child)
        self.actions.addAction(do)

    def getParent(self):
        """
        Get the Entity that has this Entity as a child. Automatically set.
        """
        return self.parent

    def setParent(self, parent):
        def do(toUpdateList):
            self.parent = parent
        self.actions.addAction(do)

    def removeFromParent(self):
        """
        Remove this Entity as a child from its parent.
        """
        def do(toUpdateList):
            if self.parent is not None:
                self.parent.removeChild(self)
                toUpdateList.append(self.parent)
        self.actions.addAction(do)

    def getChildren(self):
        return self.children

    def addChild(self, child):
        """
        Add a child. No effect until update().
        """
        def do(toUpdateList):
            self.children.append(child)
            child.removeFromParent()
            child.setParent(self)
            toUpdateList.append(child)
        self.actions.addAction(do)

    def removeChild(self, child):
        """
        Remove a child. No effect until update().
        """
        def do(toUpdateList):
            if child in self.children:
                self.children.remove(child)
                child.setParent(None)
                toUpdateList.append(child)
        self.actions.addAction(do)

    def update(self):
        return self.actions.doActions()

    def readyToRemove(self):
        return self.remove

