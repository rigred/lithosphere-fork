# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""
from __future__ import with_statement

from halogen import Widget, Column
from gletools import Sampler2D, UniformArray
from pyglet.gl import *
from .util import Output, LabelSlider, quad, nested
from .node import Node

class Simplex(Node):
    seed = [151,160,137,91,90,15,
        131,13,201,95,96,53,194,233,7,225,140,36,103,30,69,142,8,99,37,240,21,10,23,
        190, 6,148,247,120,234,75,0,26,197,62,94,252,219,203,117,35,11,32,57,177,33,
        88,237,149,56,87,174,20,125,136,171,168, 68,175,74,165,71,134,139,48,27,166,
        77,146,158,231,83,111,229,122,60,211,133,230,220,105,92,41,55,46,245,40,244,
        102,143,54, 65,25,63,161, 1,216,80,73,209,76,132,187,208, 89,18,169,200,196,
        135,130,116,188,159,86,164,100,109,198,173,186, 3,64,52,217,226,250,124,123,
        5,202,38,147,118,126,255,82,85,212,207,206,59,227,47,16,58,17,182,189,28,42,
        223,183,170,213,119,248,152, 2,44,154,163, 70,221,153,101,155,167, 43,172,9,
        129,22,39,253, 19,98,108,110,79,113,224,232,178,185, 112,104,218,246,97,228,
        251,34,242,193,238,210,144,12,191,179,162,241, 81,51,145,235,249,14,239,107,
        49,192,214, 31,181,199,106,157,184, 84,204,176,115,121,50,45,127, 4,150,254,
        138,236,205,93,222,114,67,29,24,72,243,141,128,195,78,66,215,61,156,180,
    ]

    grad = [
        +1,+1, -1,+1, +1,-1, -1,-1,
        +1,+0, -1,+0, +1,+0, -1,+0,
        +0,+1, +0,-1, +0,+1, +0,-1,
    ];

    def __init__(self, application):
        Node.__init__(self, 'Simplex', application)
        self.output = Output(self).append_to(self.column)
        self.shader = application.shader('simplex.frag',
            p       = UniformArray(int, 1, self.seed),
            grad    = UniformArray(float, 2, self.grad),
        )

        self.size = LabelSlider('Size', start=0.1).insert_before(self.output)
        self.height = LabelSlider('Height', start=0.5).insert_before(self.output)
        self.offset = LabelSlider('Offset', start=0.0).insert_before(self.output)
        self.octaves = LabelSlider('Octaves', start=0.0).insert_before(self.output)
        self.falloff = LabelSlider('Falloff', start=0.15).insert_before(self.output)
        self.step = LabelSlider('Step', start=0.8).insert_before(self.output)

        self._parameters = dict(
            size = self.size,
            height = self.height,
            offset = self.offset,
            octaves = self.octaves,
            falloff = self.falloff,
            step = self.step,
        )

    def compute(self):
        view = self.application.processing_view

        size = 1000.0 ** self.size.value - 1.0
        height = self.height.value ** 3.0
        offset = self.offset.value * 2.0
        octaves = int(self.octaves.value*20)
        falloff = 100.0 ** self.falloff.value
        step = self.step.value * 4
        
        fbo = self.application.framebuffer
        self.texture.unit = GL_TEXTURE0
        fbo.textures[0] = self.texture

        with nested(view, fbo, self.application.height_reset):
            quad(self.texture.width, self.texture.height)
           
        glEnable(GL_BLEND)
        glBlendFunc(GL_ONE, GL_ONE)
        for i in range(1, octaves+2):
            self.shader.vars['size'] = size * step**i
            self.shader.vars['offset'] = offset * step**i
            self.shader.vars['height'] = height / i**falloff

            with nested(view, fbo, self.shader):
                quad(self.texture.width, self.texture.height)
        glDisable(GL_BLEND)

nodes = [Simplex]
