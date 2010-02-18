from halogen import Slot, Dropable, Row, Label, Slider
from pyglet.graphics import draw
from pyglet.gl import *
from contextlib import nested

def slider(title, on_change, start=0):
    row = Row()
    Label(title).append_to(row)
    Slider(start=start).append_to(row).on_change = on_change
    return row

class Input(Slot):
    def __init__(self, node):
        Slot.__init__(self)
        self.node = node
        self.source = None

    def on_remove(self, connector):
        self.node.dirty = True
        self.source = None
    
    def on_drop(self, connector):
        self.node.dirty = True
        self.source = connector.output.node

class Connector(Dropable):
    target = Input
    def __init__(self, output):
        self.output = output
        Dropable.__init__(self)

    def on_drop(self, slot):
        if not slot:
            self.output.content = self

class Output(Slot):
    def __init__(self, node):
        self.connector = Connector(self)
        Slot.__init__(self, self.connector)
        node.application.canvas.add(self)
        self.node = node

def quad(top, right, bottom, left):
    glVertex3f(bottom, right, 0.0)
    glVertex3f(bottom, left, 0.0)
    glVertex3f(top, left, 0.0)
    glVertex3f(top, right, 0.0)

def quad(width, height):
    draw(4, GL_QUADS, 
        ('v2f', (
            0, 0,
            width, 0,
            width, height,
            0, height,
        )),
        ('t2f', (
            0, 0,
            1, 0,
            1, 1,
            0, 1,
        )),
    )
