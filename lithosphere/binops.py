# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from halogen import Widget, Column, Area
from gletools import Sampler2D

from .util import Output, Input, quad, nested
from pyglet.gl import *

class Binop(object):
    def __init__(self, application):
        self.application = application
        self.texture = application.create_texture()
        column = Column()
        self.op1 = Input(self).append_to(column)
        inout = Area().append_to(column).add_class('inout')
        self.op2 = Input(self).append_to(inout)
        self.output = Output(self).append_to(inout)
        self.widget = Widget(self.label, column).append_to(application.work_area)
        self.shader = application.shader(self.shader)
        self.shader.vars.op1 = Sampler2D(GL_TEXTURE0)
        self.shader.vars.op2 = Sampler2D(GL_TEXTURE1)
        self.dirty = True

    def update(self):
        if self.op1.source and self.op2.source:
            op1_updated = self.op1.source.update()
            op2_updated = self.op2.source.update()
            operands_updated = op1_updated or op2_updated

            if self.dirty or operands_updated:
                tex1 = self.op1.source.texture
                tex2 = self.op2.source.texture
                tex1.unit = GL_TEXTURE0
                tex2.unit = GL_TEXTURE1

                fbo = self.application.framebuffer
                fbo.textures[0] = self.texture

                with nested(fbo, self.shader, tex1, tex2):
                    quad(self.texture.width, self.texture.height)

                self.dirty = False
                return True

class Addition(Binop):
    label = 'Addition'
    shader = 'addition.frag'

class Multiply(Binop):
    label = 'Multiply'
    shader = 'multiply.frag'
