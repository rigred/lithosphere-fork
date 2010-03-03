# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""
from __future__ import with_statement

from halogen import Widget, Column, Area
from pyglet.gl import *
from gletools import Sampler2D

from .util import Output, Input, quad, nested, connect
from .node import Node

class Binop(Node):
    def __init__(self, application):
        Node.__init__(self, self.label, application)
        self.op1 = Input(self).append_to(self.column)
        inout = Area().append_to(self.column).add_class('inout')
        self.op2 = Input(self).append_to(inout)
        self.output = Output(self).append_to(inout)
        self.shader = application.shader(self.shader)
        self.shader.vars.op1 = Sampler2D(GL_TEXTURE0)
        self.shader.vars.op2 = Sampler2D(GL_TEXTURE1)
        self.updated = False

    def update(self):
        if self.op1.source and self.op2.source:
            self.op1.source.update()
            self.op2.source.update()
            revision = self.revision 

            if revision != self.updated:
                view = self.application.processing_view

                tex1 = self.op1.source.texture
                tex2 = self.op2.source.texture
                tex1.unit = GL_TEXTURE0
                tex2.unit = GL_TEXTURE1

                fbo = self.application.framebuffer
                fbo.textures[0] = self.texture

                with nested(view, fbo, self.shader, tex1, tex2):
                    quad(self.texture.width, self.texture.height)

                self.updated = revision

    @property
    def revision(self):
        if self.op1.source and self.op2.source:
            return hash((
                self.__class__.__name__,
                self.op1.source.revision,
                self.op2.source.revision,
            ))
        else:
            return hash(self.__class__.__name__)

    @property
    def sources(self):
        return dict(
            op1 = self.op1,
            op2 = self.op2,
        )
    
    def reconnect(self, data, instances):
        op1_id = data['op1']
        if op1_id:
            node = instances[op1_id]
            connect(node, self.op1)

        op2_id = data['op2']
        if op2_id:
            node = instances[op2_id]
            connect(node, self.op2)

class Add(Binop):
    label = 'Add'
    shader = 'addition.frag'

class Multiply(Binop):
    label = 'Multiply'
    shader = 'multiply.frag'

class Divide(Binop):
    label = 'Divide'
    shader = 'divide.frag'

class Subtract(Binop):
    label = 'Subtract'
    shader = 'subtract.frag'

class Power(Binop):
    label = 'Power'
    shader = 'power.frag'

class Max(Binop):
    label = 'Max'
    shader = 'max.frag'

class Min(Binop):
    label = 'Min'
    shader = 'min.frag'

nodes = Add, Subtract, Multiply, Power, Min, Max
