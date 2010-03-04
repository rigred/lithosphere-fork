# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""
from __future__ import with_statement
import os, sys, os

import pyglet
import pyglet.gl
from pyglet.gl import *

from halogen import Root, Area, Workspace, here, Button
from gletools import Texture, Framebuffer, ShaderProgram, FragmentShader, Viewport, Screen

from .dialogs import Dialogs
from .toolbar import Toolbar
from .terrain import Terrain
from .lines import LineCanvas
from .viewport import View3d
from .node_factory import NodeFactory
from .json_api import dump, load

class Application(object):
    def __init__(self):
        self.mesh_width = 512
        self.mesh_height = 512

        self.width = 1024
        self.height = 1024
        self.shaders = {}

        self.framebuffer = Framebuffer()
        self.window = pyglet.window.Window(fullscreen=False)
        self.window.push_handlers(self)
        glClearColor(0.3, 0.3, 0.3, 1.0)
        
        self.dialogs = Dialogs()
        self.dialogs.on_open = self.on_open
        self.dialogs.on_save = self.on_save
        
        self.root = Root(self.window, here('style/style.hss'))
        self.work_area = Area(id='sidebar').append_to(self.root)
        self.workspace = Workspace().append_to(self.work_area)
        self.canvas = LineCanvas().append_to(self.workspace)
        self.processing_view = Screen(0, 0, self.width, self.height)
        self.terrain = Terrain(self)
        self.toolbar = Toolbar(self)
        self.node_factory = NodeFactory(self)
        self.viewport = View3d(self).append_to(self.root)
        pyglet.clock.schedule_interval(self.update, 0.05)
        self.temp = self.create_texture()
        self.height_reset = self.shader('height_reset.frag')

        self.nodes = []

    def add_node(self, node):
        self.nodes.append(node)

    def remove_node(self, node):
        self.nodes.remove(node)

    def on_open(self, filename):
        if os.path.isdir(filename):
            return

        with open(filename) as file:
            data = load(file)

        self.empty()

        instances = dict()
        nodes_data = dict()
        for id, node_data in data['nodes'].items():
            instances[id] = self.node_factory.create(node_data)
            nodes_data[id] = node_data

        for id, instance in instances.items():
            node_data = nodes_data[id]
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
        if terrain:
            data['terrain'] = dict(
                offset = dict(x=terrain.widget.rect.x, y = terrain.widget.rect.y),
                source = str(id(terrain.input.source)) if terrain.input.source else None
            )

        data['workspace'] = dict(
            offset = dict(x=self.workspace.xoff, y=self.workspace.yoff)
        )

        with open(filename, 'w') as file:
            dump(data, file, sort_keys=True, indent=4)

    def run(self):
        pyglet.app.run()

    def empty(self):
        for node in list(self.nodes):
            node.delete()
    
    def on_draw(self):
        self.window.clear()
        self.viewport.draw_terrain()
        self.root.draw()
        glColor4f(1.0, 1.0, 1.0, 1.0)

    def create_texture(self):
        #return Texture(self.width, self.height, format=GL_LUMINANCE32F_ARB, clamp='st')
        return Texture(self.width, self.height, format=GL_RGBA32F, clamp='st')

    def shader(self, *names):
        if names in self.shaders:
            return self.shaders[names]
        else:
            shader = ShaderProgram(*[
                FragmentShader.open(here('shaders/%s' % name))
                if name.endswith('.frag') else
                VertexShader.open(here('shaders/%s' % name))
                for name in names
            ])
            self.shaders[names] = shader
            return shader

    def update(self, delta):
        self.terrain.update()

def main():
    application = Application()
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if os.path.exists(path):
            application.on_open(path)
    application.run()
