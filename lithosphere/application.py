# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

import pyglet
from pyglet.gl import *

from halogen import Root, Area, here
from gletools import Texture, Framebuffer, ShaderProgram, FragmentShader

from .toolbar import Toolbar
from .terrain import Terrain
from .lines import LineCanvas
from .viewport import Viewport

from .noise import Random, Simplex
from .binops import Addition, Multiply

class Application(object):
    def __init__(self):
        self.width = 512
        self.height = 512
        self.shaders = {}

        self.framebuffer = Framebuffer()
        self.window = pyglet.window.Window(fullscreen=True, vsync=False)
        self.window.push_handlers(self)
        glClearColor(0.3, 0.3, 0.3, 1.0)
        self.root = Root(self.window, here('style/style.hss'))
        self.work_area = Area(id='sidebar').append_to(self.root)
        self.canvas = LineCanvas().append_to(self.work_area)
        self.terrain = Terrain(self)
        self.toolbar = Toolbar(self)
        self.toolbar.add(Random)
        self.toolbar.add(Simplex)
        self.toolbar.add(Addition)
        self.toolbar.add(Multiply)
        self.viewport = Viewport(self).append_to(self.root)
        pyglet.clock.schedule_interval(self.update, 0.05)

    def run(self):
        pyglet.app.run()
    
    def on_draw(self):
        self.window.clear()
        self.viewport.draw_terrain()
        self.root.draw()

    def create_texture(self):
        return Texture(self.width, self.height, format=GL_LUMINANCE32F_ARB)

    def shader(self, name):
        if name in self.shaders:
            return self.shaders[name]
        else:
            shader = ShaderProgram(
                FragmentShader.open(here('shaders/%s' % name))
            )
            self.shaders[name] = shader
            return shader

    def update(self, delta):
        self.terrain.update()

def main():
    application = Application()
    application.run()
