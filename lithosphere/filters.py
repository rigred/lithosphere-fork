# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from halogen import Widget, Column, Area
from gletools import Sampler2D
from pyglet.gl import *

from .util import Output, InputSlot, quad, LabelSlider, LabelCheckbox, connect, LabelInput
from .node import Node

class Base(Node):
    def __init__(self, application):
        Node.__init__(self, self.label, application)
        self.inout = Area().append_to(self.column).add_class('inout')
        self.input = InputSlot(self).append_to(self.inout)
        self.output = Output(self).append_to(self.inout)
        self.updated = False
        
        self.shader = application.shader(self.shader)
        self.shader.vars.texture = Sampler2D(GL_TEXTURE0)
        self.shader.vars.offsets = 1.0/self.texture.width, 1.0/self.texture.height

        self._parameters = dict()
    
    @property
    def revision(self):
        sources = tuple([input.source.revision if input.source else None for input in self.sources.values()])
        parameters = tuple((name, param.value) for name, param in self._parameters.items())
        return hash((self.__class__.__name__, parameters, sources))
    
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
        self.weight = LabelInput('Weight', self).insert_before(self.inout)
        self._parameters['repeat'] = self.repeat
        self.last_repeat = 0
        self.last_source_revision = None
        self.shader.vars.texture = Sampler2D(GL_TEXTURE0)
        self.shader.vars.filter_weight = Sampler2D(GL_TEXTURE1)
    
    def update(self):
        if self.input.source:
            self.input.source.update()
            if self.weight.input.source:
                self.weight.input.source.update()

            revision = self.revision

            if revision != self.updated:
                self.compute()
                self.updated = revision
                return True
    
    def reconnect(self, data, instances):
        input_id = data['input']
        if input_id:
            node = instances[input_id]
            connect(node, self.input)

        weight_id = data.get('weight')
        if weight_id:
            node = instances[weight_id]
            connect(node, self.weight.input)

    def compute(self):
        repeat = int(self.repeat.value*100)
        source_revision = self.input.source.revision
        self.update_shader()
        shader = self.shader
        input = self.input.source.texture
        output = self.texture
        if self.weight.input.source:
            weight = (self.weight.input.source.texture,)
        else:
            weight = ()

        tmp = self.application.temp

        if repeat > self.last_repeat and self.last_source_revision == source_revision:
            delta = repeat - self.last_repeat
            for i in range(delta):
                self.apply(shader, tmp, output, *weight)
                self.apply(shader, output, tmp, *weight)

        else:
            self.apply(shader, output, input, *weight)
            for i in range(repeat):
                self.apply(shader, tmp, output, *weight)
                self.apply(shader, output, tmp, *weight)
        
        self.last_repeat = repeat
        self.last_source_revision = source_revision
    
    @property
    def sources(self):
        return dict(
            weight = self.weight.input,
            input = self.input,
        )
    
class Gaussian(Repeatable):
    label = 'Gaussian' 
    shader = 'gaussian.frag'

class Erode(Repeatable):
    label = 'Erode'
    shader = 'erode.frag'

    def __init__(self, application):
        Repeatable.__init__(self, application) 
        self.slope = LabelCheckbox('Slope', checked=True).insert_before(self.inout)
        self.shallow = LabelCheckbox('Shallow', checked=False).insert_before(self.inout)
        self.invert = LabelCheckbox('Invert', checked=False).insert_before(self.inout)
        self.rough = LabelCheckbox('Rough', checked=False).insert_before(self.inout)
        
        self._parameters['slope'] = self.slope
        self._parameters['shallow'] = self.shallow
        self._parameters['invert'] = self.invert
        self._parameters['rough'] = self.rough
    
    def update_shader(self):
        self.shader.vars.invert = self.invert.value
        self.shader.vars.shallow = self.shallow.value
        self.shader.vars.rough = self.rough.value
        self.shader.vars.slope = self.slope.value

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
    shader = 'incline.frag'

    def __init__(self, application):
        Base.__init__(self, application)
        self.invert = LabelCheckbox('Invert').insert_before(self.inout)
        self.factor = LabelSlider('Factor', start=0.5).insert_before(self.inout)
        self.offset = LabelSlider('Offset', start=0.5).insert_before(self.inout)
        self._parameters['invert'] = self.invert
        self._parameters['factor'] = self.factor
        self._parameters['offset'] = self.offset

    def update_shader(self):
        self.shader.vars.invert = self.invert.value
        self.shader.vars.factor = (self.factor.value * 2) ** 10
        self.shader.vars.offset = (self.offset.value-0.5) * 10

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

nodes = [Gaussian, Erode, Incline, Step, Wind]
