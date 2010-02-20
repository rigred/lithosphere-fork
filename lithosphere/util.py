from halogen import Slot, Dropable, Row, Label, Slider
from pyglet.graphics import draw
from pyglet.gl import *
from contextlib import nested

class LabelSlider(Row):
    def __init__(self, title, start):
        Row.__init__(self)
        Label(title).append_to(self)
        self.slider = Slider(start=start).append_to(self)

    @property
    def value(self):
        return self.slider.value

def slider(title, on_change=None, start=0):
    row = Row()
    Label(title).append_to(row)
    instance = Slider(start=start).append_to(row)
    instance.on_change = on_change
    return row

class Input(Slot):
    def __init__(self, node):
        Slot.__init__(self)
        self.node = node
        self.source = None

    def on_remove(self, connector):
        self.source = None
    
    def on_drop(self, connector):
        self.source = connector.output.node

class Connector(Dropable):
    target = Input
    def __init__(self, output):
        self.output = output
        application = output.node.application
        self.canvas = application.canvas
        self.canvas.add(self)
        Dropable.__init__(self, layer=application.workspace)

    def on_drop(self, slot):
        if not self.output.content:
            self.output.content = Connector(self.output)

        if not slot:
            self.canvas.remove(self)

class Output(Slot):
    def __init__(self, node):
        self.node = node
        Slot.__init__(self)
        self.content = Connector(self)

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
