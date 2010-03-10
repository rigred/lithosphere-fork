# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""
from __future__ import with_statement

from contextlib import nested

from pyglet.gl import *
from halogen import hsl2rgb
from .util import Output, LabelSlider, quad
from .node import Node

class Color(Node):
    def __init__(self, application):
        Node.__init__(self, 'Color', application)
        self.output = Output(self).append_to(self.column)
        self.hue = LabelSlider('Hue', 0.5).insert_before(self.output)
        self.saturdation = LabelSlider('Sat.', 0.5).insert_before(self.output)
        self.lightness = LabelSlider('Light', 0.5).insert_before(self.output)
        self.updated = False

    def update(self):
        view = self.application.processing_view
        revision = self.revision
        if revision != self.updated:
            fbo = self.application.framebuffer
            self.texture.unit = GL_TEXTURE0
            fbo.textures[0] = self.texture
            color = hsl2rgb(self.hue.value, self.saturdation.value, self.lightness.value)
            
            with nested(view, fbo):
                glColor3f(*color)
                quad(self.texture.width, self.texture.height)

            self.updated = revision
        
    @property
    def revision(self):
        return hash((self.hue.value, self.saturdation.value, self.lightness.value))

nodes = [Color]
