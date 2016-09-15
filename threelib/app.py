__author__ = "jacobvanthoog"


class AppInstance:

    def getFps(self):
        return None

    def windowWidth(self):
        return None
    
    def windowHeight(self):
        return None

    def getAspect(self):
        return None

    def getFOV(self):
        return None

    def buttonPressed(self, button=0):
        return False

    def shiftPressed(self):
        return False

    def ctrlPressed(self):
        return False

    def altPressed(self):
        return False

    def mouseX(self):
        return None

    def mouseY(self):
        return None

    def lockMouse(self):
        pass

    def unlockMouse(self):
        pass
        

class AppInterface:

    def setAppInstance(self, instance):
        pass

    def init(self):
        pass
        
    def draw(self):
        pass

    def keyPressed(self, key):
        pass
    
    def keyReleased(self, key):
        pass
        
    def mousePressed(self, button, mouseX, mouseY):
        pass
        
    def mouseReleased(self, button, mouseX, mouseY):
        pass
    
    def mouseMoved(self, mouseX, mouseY, pmouseX, pmouseY):
        pass

