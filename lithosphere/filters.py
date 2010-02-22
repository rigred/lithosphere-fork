# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from halogen import Widget, Column, Area
from gletools import Sampler2D
from pyglet.gl import *

from .util import Output, Input, quad, nested, LabelSlider, connect
from .node import Node

class Base(Node):
    def __init__(self, application):
        Node.__init__(self, self.label, application)
        self.inout = Area().append_to(self.column).add_class('inout')
        self.input = Input(self).append_to(self.inout)
        self.output = Output(self).append_to(self.inout)
        self.repeat = LabelSlider('Repeat', start=0.0).insert_before(self.inout)
        self.updated = False
        
        self.shader = application.shader(self.shader)
        self.shader.vars.texture = Sampler2D(GL_TEXTURE0)
        self.shader.vars.offsets = 1.0/self.texture.width, 1.0/self.texture.height
    
    @property
    def revision(self):
        if self.input.source:
            return hash((self.__class__.__name__, self.repeat.value, self.input.source.revision))
        else:
            return hash((self.__class__.__name__, self.repeat.value))
    
    def get_parameters(self):
        return dict(repeat=self.repeat.value)
    def set_parameters(self, values):
        self.repeat.value = values['repeat']

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
                view = self.application.processing_view
                input = self.input.source.texture
                input.unit = GL_TEXTURE0
                output = self.texture
                output.unit = GL_TEXTURE0
                temp = self.application.temp
                temp.unit = GL_TEXTURE0
                shader = self.shader

                fbo = self.application.framebuffer
                fbo.textures[0] = output
                with nested(view, fbo, shader, input):
                    quad(output.width, output.height)
                
                for i in range(int(self.repeat.value*100.0)):
                    fbo.textures[0] = temp
                    with nested(view, fbo, shader, output):
                        quad(output.width, output.height)
                    
                    fbo.textures[0] = output
                    with nested(view, fbo, shader, temp):
                        quad(output.width, output.height)

                self.updated = revision
                return True
    
class Gaussian(Base):
    label = 'Gaussian' 
    shader = 'gaussian.frag'

class Erode(Base):
    label = 'Erode'
    shader = 'erode.frag'

class Steep(Base):
    label = 'Steep'
    shader = 'steep.frag'
    
        
nodes = Gaussian, Erode, Steep
