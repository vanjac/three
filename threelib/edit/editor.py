__author__ = "vantjac"

from threelib.edit.editorMain import *

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

def keyPressed(key, mouseX, mouseY):
    print("Key pressed:", key)
    if key == b'q':
        sys.exit()

def keyReleased(key, mouseX, mouseY):
    print("Key released:", key)

# mouse buttons: left=0, middle=1, right=2, 
#   scroll-up=3, scroll-down=4, scroll-left=5, scroll-right=6
def mousePressed(button, mouseX, mouseY):
    print("Mouse pressed:", button, mouseX, mouseY)

def mouseReleased(button, mouseX, mouseY):
    print("Mouse released:", button, mouseX, mouseY)

# info passed as tuple: (mouseX, mouseY)
def mouseMoved(mouseX, mouseY):
    print("Mouse moved:", mouseX, mouseY)

def draw():
    glTranslate(0, 0, -5)
    glRotate(30, 0, 1, 0)
    
    glBegin(GL_TRIANGLES)
    glColor(1.0, 0.0, 0.0)
    glVertex(0.0, 1.0, 0.0)
    glColor(0.0, 1.0, 0.0)
    glVertex(1.0, -1.0, 0.0)
    glColor(0.0, 0.0, 1.0)
    glVertex(-1.0, -1.0, 0.0)
    glEnd()
