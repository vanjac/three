
def makePlayer():
    forwardButtonAxis = ButtonAxis(world.buttonInputs['w'], 0.0, 1.0)
    backButtonAxis = ButtonAxis(world.buttonInputs['s'], 0.0, 1.0)
    leftButtonAxis = ButtonAxis(world.buttonInputs['a'], 0.0, 1.0)
    rightButtonAxis = ButtonAxis(world.buttonInputs['d'], 0.0, 1.0)
    
    xWalkAxis = AxisScale(
        AxisSum(rightButtonAxis, AxisOpposite(leftButtonAxis)), 50.0)
    yWalkAxis = AxisScale(
        AxisSum(forwardButtonAxis, AxisOpposite(backButtonAxis)), 50.0)
    
    player = FirstPersonPlayer( world,
                                AxisScale(world.axisInputs['mouse-x'], .005),
                                AxisScale(world.axisInputs['mouse-y'], .005),
                                xWalkAxis, yWalkAxis )
    world.camera = player
    return player

