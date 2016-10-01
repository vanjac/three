
def makePlayer():
    camera = FirstPersonCamera( AxisScale(world.axisInputs['mouse-y'], .005) )
    world.simulator.addObject(camera)
    world.camera = camera
    
    forwardButtonAxis = ButtonAxis(world.buttonInputs['w'], 0.0, 1.0)
    backButtonAxis = ButtonAxis(world.buttonInputs['s'], 0.0, 1.0)
    leftButtonAxis = ButtonAxis(world.buttonInputs['a'], 0.0, 1.0)
    rightButtonAxis = ButtonAxis(world.buttonInputs['d'], 0.0, 1.0)
    
    xWalkAxis = AxisScale(
        AxisSum(rightButtonAxis, AxisOpposite(leftButtonAxis)), 1.0)
    yWalkAxis = AxisScale(
        AxisSum(forwardButtonAxis, AxisOpposite(backButtonAxis)), 1.0)
    
    player = FirstPersonPlayer( AxisScale(world.axisInputs['mouse-x'], .005),
                                xWalkAxis, yWalkAxis )
    player.addChild(camera)
    return player

