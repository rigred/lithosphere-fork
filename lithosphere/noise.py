# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from halogen import Widget, Column
from gletools import Sampler2D
from pyglet.gl import *
from .util import Output, LabelSlider, quad, nested

class Simplex(object):
    def __init__(self, application):
        self.application = application
        self.texture = application.create_texture()
        self.column = Column()
        self.output = Output(self).append_to(self.column)
        self.widget = Widget('Simplex', self.column).add_class('node').append_to(application.workspace)
        self.shader = application.shader('simplex.frag')
        self.shader.vars.texture = Sampler2D(GL_TEXTURE0)

        self.size = LabelSlider('Size', start=0.1).insert_before(self.output)
        self.height = LabelSlider('Height', start=0.5).insert_before(self.output)
        self.offset = LabelSlider('Offset', start=0.0).insert_before(self.output)
        self.octaves = LabelSlider('Octaves', start=0.0).insert_before(self.output)
        self.falloff = LabelSlider('Falloff', start=0.15).insert_before(self.output)
        self.step = LabelSlider('Step', start=0.8).insert_before(self.output)
        self.updated = False

    def update(self):
        revision = self.revision
        if revision != self.updated:
            size = 1000.0 ** self.size.value - 1.0
            height = self.height.value ** 3.0
            offset = self.offset.value * 2.0
            octaves = int(self.octaves.value*20)
            falloff = 100.0 ** self.falloff.value
            step = self.step.value * 4
            
            fbo = self.application.framebuffer
            self.texture.unit = GL_TEXTURE0
            fbo.textures[0] = self.texture

            with nested(fbo, self.application.height_reset):
                quad(self.texture.width, self.texture.height)
                
            for i in range(1, octaves+2):
                self.shader.vars['size'] = size * step**i
                self.shader.vars['offset'] = offset * step**i
                self.shader.vars['height'] = height / i**falloff

                with nested(self.texture, fbo, self.shader):
                    quad(self.texture.width, self.texture.height)

            self.updated = revision
   
    @property
    def revision(self):
        return hash((
            self.__class__.__name__,
            self.size.value,
            self.offset.value,
            self.height.value,
            self.octaves.value,
            self.falloff.value,
            self.step.value,
        ))
