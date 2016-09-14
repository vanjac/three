__author__ = "jacobvanthoog"

class SimObject:
    
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