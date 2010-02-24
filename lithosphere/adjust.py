# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from halogen import Area
from gletools import Sampler2D
from pyglet.gl import *

from .util import Output, Input, quad, nested, LabelSlider, connect
from .node import Node

class Adjust(Node):
    def __init__(self, application):
        Node.__init__(self, 'Adjust', application)
        self.inout = Area().append_to(self.column).add_class('inout')
        self.input = Input(self).append_to(self.inout)
        self.output = Output(self).append_to(self.inout)
        
        self.shader = application.shader('adjust.frag')
        self.shader.vars.texture = Sampler2D(GL_TEXTURE0)
        
        self.factor = LabelSlider('Factor', start=0.1).insert_before(self.inout)
        self.offset = LabelSlider('Offset', start=0.5).insert_before(self.inout)

        self.updated = False
    
    @property
    def revision(self):
        if self.input.source:
            return hash((self.__class__.__name__,
                self.factor.value,
                self.offset.value,
                self.input.source.revision
            ))
        else:
            return hash((self.__class__.__name__,
                self.factor.value,
                self.offset.value
            ))
    
    def get_parameters(self):
        return dict(
            factor  = self.factor.value,
            offset  = self.offset.value,
        )
    def set_parameters(self, values):
        self.factor.value = values['factor']
        self.offset.value = values['offset']

    parameters = property(get_parameters, set_parameters)
    del get_parameters, set_parameters
    
    @property
    def sources(self):
        return dict(input=self.input)

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
                shader = self.shader

                shader.vars.factor = self.factor.value * 10
                shader.vars.offset = (self.offset.value-0.5) * 10

                fbo = self.application.framebuffer
                fbo.textures[0] = output
                with nested(view, fbo, shader, input):
                    quad(output.width, output.height)
                
                self.updated = revision
    
nodes = [Adjust]
