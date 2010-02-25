# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from halogen import Widget, Column, Area
from gletools import Sampler2D
from pyglet.gl import *

from .util import Output, Input, quad, LabelSlider, LabelCheckbox, connect
from .node import Node

class Base(Node):
    def __init__(self, application):
        Node.__init__(self, self.label, application)
        self.inout = Area().append_to(self.column).add_class('inout')
        self.input = Input(self).append_to(self.inout)
        self.output = Output(self).append_to(self.inout)
        self.updated = False
        
        self.shader = application.shader(self.shader)
        self.shader.vars.texture = Sampler2D(GL_TEXTURE0)
        self.shader.vars.offsets = 1.0/self.texture.width, 1.0/self.texture.height

        self._parameters = dict()
    
    @property
    def revision(self):
        source_revision = self.input.source.revision if self.input.source else None
        parameters = tuple((name, param.value) for name, param in self._parameters.items())
        return hash((self.__class__.__name__, source_revision, parameters))
    
    def get_parameters(self):
        return dict((name, param.value) for name, param in self._parameters.items())
    def set_parameters(self, values):
        for name, value in values.items():
            self._parameters[name].value = value

    parameters = property(get_parameters, set_parameters)
    del get_parameters, set_parameters
    
    @property
    def sources(self):
        return dict(
            input = self.input,
        )

    def reconnect(self, data, instances):
        input_id = data['input']
        if input_id:
            node = instances[input_id]
            connect(node, self.input)
    
    def update(self):
        if self.input.source:
            self.input.source.update()
            revision = self.revision

            if revision != self.updated:
                self.compute()
                self.updated = revision
                return True

    def update_shader(self):
        pass
    
    def compute(self):
        self.update_shader()
        shader = self.shader
        input = self.input.source.texture
        output = self.texture
        self.apply(shader, output, input)

class Repeatable(Base):
    def __init__(self, application):
        Base.__init__(self, application)
        self.repeat = LabelSlider('Repeat', start=0.0).insert_before(self.inout)
        self._parameters['repeat'] = self.repeat

    def compute(self):
        self.update_shader()
        shader = self.shader
        input = self.input.source.texture
        output = self.texture
        tmp = self.application.temp
        self.apply(shader, output, input)
        
        for i in range(int(self.repeat.value*100.0)):
            self.apply(shader, tmp, output)
            self.apply(shader, output, tmp)
    
class Gaussian(Repeatable):
    label = 'Gaussian' 
    shader = 'gaussian.frag'

class Erode(Repeatable):
    label = 'Erode'
    shader = 'erode.frag'

    def __init__(self, application):
        Repeatable.__init__(self, application) 
        self.shallow = LabelCheckbox('Shallow', checked=False).insert_before(self.inout)
        self._parameters['shallow'] = self.shallow
        self.invert = LabelCheckbox('Invert', checked=False).insert_before(self.inout)
        self._parameters['invert'] = self.invert
        self.rough = LabelCheckbox('Rough', checked=False).insert_before(self.inout)
        self._parameters['rough'] = self.rough
    
    def update_shader(self):
        self.shader.vars.invert = self.invert.value
        self.shader.vars.shallow = self.shallow.value
        self.shader.vars.rough = self.rough.value

class Wind(Repeatable):
    label = 'Wind'
    shader = 'wind.frag'
    
    def __init__(self, application):
        Repeatable.__init__(self, application) 
        self.direction = LabelSlider('Dir', start=0.0).insert_before(self.inout)
        self.strengh = LabelSlider('Strengh', start=0.5).insert_before(self.inout)
        self.strengh2 = LabelSlider('Strengh2', start=0.5).insert_before(self.inout)
        self._parameters['direction'] = self.direction
        self._parameters['strengh'] = self.strengh
        self._parameters['strengh2'] = self.strengh2
    
    def update_shader(self):
        self.shader.vars.direction = self.direction.value
        self.shader.vars.strengh = self.strengh.value * 1.35
        self.shader.vars.strengh2 = self.strengh2.value * 2.0

class Incline(Base):
    label = 'Incline'
    shader = 'steep.frag'

    def __init__(self, application):
        Base.__init__(self, application)
        self.invert = LabelCheckbox('Invert').insert_before(self.inout)
        self._parameters['invert'] = self.invert

    def update_shader(self):
        self.shader.vars.invert = self.invert.value

class Step(Base):
    label = 'Step'
    shader = 'step.frag'
    
    def __init__(self, application):
        Base.__init__(self, application)
        self.bottom = LabelSlider('Bottom', start=0.25).insert_before(self.inout)
        self.height = LabelSlider('Hight', start=1.0).insert_before(self.inout)
        self._parameters['bottom'] = self.bottom
        self._parameters['height'] = self.height

    def update_shader(self):
        self.shader.vars.low = self.bottom.value-0.25
        self.shader.vars.high = self.bottom.value + self.height.value
    
nodes = Gaussian, Erode, Incline, Step, Wind
