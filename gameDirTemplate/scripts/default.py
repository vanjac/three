
def makePlayer():
    return FirstPersonCamera(AxisInputScale(world.axisInputs['mouse-x'], .005),
                             AxisInputScale(world.axisInputs['mouse-y'], .005))
