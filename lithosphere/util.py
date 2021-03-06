# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from halogen import Slot, Dropable, Row, Label, Slider, Checkbox
from pyglet.graphics import draw
from pyglet.gl import *
from contextlib import nested

class LabelSlider(Row):
    def __init__(self, title, start):
        Row.__init__(self)
        Label(title).append_to(self)
        self.slider = Slider(start=start).append_to(self)

    def get_value(self):
        return self.slider.value
    def set_value(self, value):
        self.slider.value = value
    value = property(get_value, set_value)
    del get_value, set_value

class LabelCheckbox(Row):
    def __init__(self, title, checked=False):
        Row.__init__(self)
        Label(title).append_to(self)
        self.checkbox = Checkbox(checked=checked).append_to(self)
    
    def get_value(self):
        return self.checkbox.checked
    def set_value(self, checked):
        if checked:
            self.checkbox.check()
        else:
            self.checkbox.uncheck()
    value = property(get_value, set_value)

class InputSlot(Slot):
    def __init__(self, node):
        Slot.__init__(self)
        self.node = node
        self.source = None

    def on_remove(self, connector):
        self.source = None
        connector.input = None
    
    def on_drop(self, connector):
        self.source = connector.output.node
        connector.input = self

class LabelInput(Row):
    def __init__(self, title, node):
        Row.__init__(self)
        self.input = InputSlot(node).append_to(self)
        Label(title).append_to(self)

    def get_node(self):
        return self.input.node
    def set_node(self, node):
        self.input.node = node
    node = property(get_node, set_node)

    def get_source(self):
        return self.input.source
    def set_source(self, source):
        self.input.source = source
    source = property(get_source, set_source)

    def get_content(self):
        return self.input.content
    def set_content(self, content):
        self.input.content = content 
    content = property(get_content, set_content)

    def drop(self, connector):
        self.input.drop(connector)

class Connector(Dropable):
    target = InputSlot
    def __init__(self, output):
        self.input = None
        self.output = output
        self.output.connections.append(self)
        application = output.node.application
        self.canvas = application.canvas
        self.canvas.add(self)
        Dropable.__init__(self, layer=application.workspace)

    def find_slots(self):
        slots = Dropable.find_slots(self)
        nodes = self.output.node.branch_nodes
        return [slot for slot in slots if slot.node not in nodes]

    def on_drop(self, slot):
        if not self.output.content:
            self.output.content = Connector(self.output)

        if not slot:
            self.delete()

    def delete(self):
        self.canvas.remove(self)
        self.output.connections.remove(self)
        if self.parent:
            self.remove()
        if self.input:
            self.input.on_remove(self)

class Output(Slot):
    def __init__(self, node):
        Slot.__init__(self)
        self.node = node
        self.connections = []
        self.content = Connector(self)

    def delete(self):
        for connection in list(self.connections):
            connection.delete()

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

def connect(node, input):
    connector = Connector(node.output)
    input.drop(connector)
