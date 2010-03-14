# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""
from __future__ import with_statement

from halogen import Area
from gletools import Sampler2D
from pyglet.gl import *

from .util import Output, InputSlot, quad, nested, LabelSlider
from .node import Node

class Adjust(Node):
    def __init__(self, application):
        Node.__init__(self, 'Adjust', application)
        self.inout = Area().append_to(self.column).add_class('inout')
        self.input = InputSlot(self).append_to(self.inout)
        self.output = Output(self).append_to(self.inout)
        
        self.shader = application.shader('adjust.frag')
        self.shader.vars.texture = Sampler2D(GL_TEXTURE0)
        
        self.factor = LabelSlider('Factor', start=0.5).insert_before(self.inout)
        self.offset = LabelSlider('Offset', start=0.5).insert_before(self.inout)

        self._parameters = dict(
            factor = self.factor,
            offset = self.offset,
        )
        self.sources = dict(
            input = self.input,
        )
    
    def compute(self):
        view = self.application.processing_view
        input = self.input.source.texture
        input.unit = GL_TEXTURE0
        output = self.texture
        output.unit = GL_TEXTURE0
        shader = self.shader

        shader.vars.factor = (self.factor.value * 2) ** 10
        shader.vars.offset = (self.offset.value-0.5) * 10

        fbo = self.application.framebuffer
        fbo.textures[0] = output
        with nested(view, fbo, shader, input):
            quad(output.width, output.height)
                
    
nodes = [Adjust]
