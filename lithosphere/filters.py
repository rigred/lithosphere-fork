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

class Steep(Base):
    label = 'Steep'
    shader = 'steep.frag'

    def __init__(self, application):
        Base.__init__(self, application)
        self.invert = LabelCheckbox('Invert').insert_before(self.inout)
        self._parameters['invert'] = self.invert

    def update_shader(self):
        self.shader.vars.invert = self.invert.value
    
nodes = Gaussian, Erode, Steep
