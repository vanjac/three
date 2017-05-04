
def makePlayer():
    player = FirstPersonPlayer( world,
                                world.axisInputs['x_look'],
                                world.axisInputs['y_look'],
                                world.axisInputs['x_walk'],
                                world.axisInputs['y_walk'],
                                world.buttonInputs['jump'])
    world.camera = player
    return player

def makeFlyingPlayer():
    player = FirstPersonFlyingPlayer( world,
                                      world.axisInputs['x_look'],
                                      world.axisInputs['y_look'],
                                      world.axisInputs['x_walk'],
                                      world.axisInputs['y_walk'])
    world.camera = player
    return player
    

def use():
    cam = world.camera
    
    def getMeshCallback(mesh, face):
        if mesh is not None:
            mesh.doUseAction()
            
    world.getFaceAtRay( getMeshCallback, cam.getPosition(),
                        Vector(1.0, 0.0, 0.0).rotate(cam.getRotation()) )

class UseScanner(SimObject):

    def __init__(self, button):
        self.button = button

    def scan(self, timeElapsed, totalTime):
        event = self.button.getEvent()
        if event == ButtonInput.PRESSED_EVENT:
            use()

world.simulator.addObject(UseScanner(world.buttonInputs['use']))

