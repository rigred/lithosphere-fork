# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

import pyglet
from pyglet.gl import *

from halogen import Root, Area, Workspace, here
from gletools import Texture, Framebuffer, ShaderProgram, FragmentShader

from .toolbar import Toolbar
from .terrain import Terrain
from .lines import LineCanvas
from .viewport import Viewport

from .noise import Simplex
from .binops import Add, Multiply
from .filters import Gaussian, Erode

class Application(object):
    def __init__(self):
        self.width = 256
        self.height = 256
        self.shaders = {}

        self.framebuffer = Framebuffer()
        self.window = pyglet.window.Window(fullscreen=True, vsync=False)
        self.window.push_handlers(self)
        glClearColor(0.3, 0.3, 0.3, 1.0)
        self.root = Root(self.window, here('style/style.hss'))
        self.work_area = Area(id='sidebar').append_to(self.root)
        self.workspace = Workspace().append_to(self.work_area)
        self.canvas = LineCanvas().append_to(self.workspace)
        self.terrain = Terrain(self)
        self.toolbar = Toolbar(self)
        self.fill_toolbar()
        self.viewport = Viewport(self).append_to(self.root)
        pyglet.clock.schedule_interval(self.update, 0.05)
        self.temp = self.create_texture()
        self.height_reset = self.shader('height_reset.frag')

    def fill_toolbar(self):
        add = self.toolbar.add
        add(Simplex)
        add(Add)
        add(Multiply)
        add(Gaussian)
        add(Erode)

    def run(self):
        pyglet.app.run()
    
    def on_draw(self):
        self.window.clear()
        self.viewport.draw_terrain()
        self.root.draw()

    def create_texture(self):
        return Texture(self.width, self.height, format=GL_LUMINANCE32F_ARB, clamp='st')

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
