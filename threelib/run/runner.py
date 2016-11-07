__author__ = "jacobvanthoog"


class GameRunner:

    def __init__(self, simulator, realTime):
        self.simulator = simulator
        self.speed = 1.0
        self.isPaused = False
        self.lastRealTime = realTime
        self.gameTime = 0.0

    def setSimulationSpeed(self, speed):
        self.speed = speed
        if not self.isPaused:
            self.simulator.setSimulationSpeed(speed)

    def pause(self):
        self.isPaused = True
        self.simulator.setSimulationSpeed(0.0)

    def unpause(self):
        self.isPaused = False
        self.simulator.setSimulationSpeed(self.speed)

    def tick(self, realTime):
        lastGameTime = self.gameTime
        if not self.isPaused:
            self.gameTime += (realTime - self.lastRealTime) * self.speed
        self.lastRealTime = realTime

        self.simulator.scan(self.gameTime - lastGameTime, self.gameTime)
        self.simulator.update()

