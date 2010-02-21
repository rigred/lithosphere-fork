# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""
import json, os

import pyglet
import pyglet.gl
from pyglet.gl import *

from halogen import Root, Area, Workspace, here, Button
from gletools import Texture, Framebuffer, ShaderProgram, FragmentShader

from .dialogs import Dialogs
from .toolbar import Toolbar
from .terrain import Terrain
from .lines import LineCanvas
from .viewport import Viewport
from .node_factory import NodeFactory

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
        self.workspace = Workspace().append_to(self.work_area)
        self.canvas = LineCanvas().append_to(self.workspace)
        self.terrain = Terrain(self)
        self.toolbar = Toolbar(self)
        self.node_factory = NodeFactory(self)
        self.viewport = Viewport(self).append_to(self.root)
        pyglet.clock.schedule_interval(self.update, 0.05)
        self.temp = self.create_texture()
        self.height_reset = self.shader('height_reset.frag')

        self.dialogs = Dialogs()
        self.dialogs.on_open = self.on_open
        self.dialogs.on_save = self.on_save

        Button('Open').append_to(self.toolbar.column).on_click = self.dialogs.open
        Button('Save').append_to(self.toolbar.column).on_click = self.dialogs.save
        Button('New').append_to(self.toolbar.column).on_click = self.empty

        self.nodes = []

    def add_node(self, node):
        self.nodes.append(node)

    def on_open(self, filename):
        if os.path.isdir(filename):
            return

        with open(filename) as file:
            data = json.load(file)

        self.empty()

        instances = dict()
        for id, node_data in data['nodes'].items():
            instances[id] = self.node_factory.create(node_data)

        for instance, (id, node_data) in zip(instances.values(), data['nodes'].items()):
            instance.reconnect(node_data['sources'], instances)

        self.terrain.open(data['terrain'], instances)
        
        workspace_off = data['workspace']['offset']
        self.workspace.xoff, self.workspace.yoff = workspace_off['x'], workspace_off['y']
        
        self.viewport.pos.xyz = data['viewport']['position']
        self.viewport.rotation.xyz = data['viewport']['rotation']

    def on_save(self, filename):
        if os.path.isdir(filename):
            return
        if not filename.endswith('.lth'):
            filename += '.lth'

        data = dict(
            viewport = dict(
                rotation = list(self.viewport.rotation),
                position = list(self.viewport.pos),
            )
        )
        
        data['nodes'] = nodes = dict()
        for node in self.nodes:
            nodes[id(node)] = dict(
                type = node.__class__.__name__,
                offset = dict(x=node.widget.rect.x, y=node.widget.rect.y),
                parameters = node.parameters,
                sources = dict(
                    (name, (str(id(slot.source)) if slot.source else None))
                    for name, slot in node.sources.items()
                )
            )

        terrain = self.terrain
        if terrain.input.source:
            data['terrain'] = dict(
                offset = dict(x=terrain.widget.rect.x, y = terrain.widget.rect.y),
                source = str(id(terrain.input.source)) if terrain.input.source else None
            )

        data['workspace'] = dict(
            offset = dict(x=self.workspace.xoff, y=self.workspace.yoff)
        )

        with open(filename, 'w') as file:
            json.dump(data, file, sort_keys=True, indent=4)

    def run(self):
        pyglet.app.run()

    def empty(self):
        for node in self.nodes:
            node.delete()
        self.nodes = []
    
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
