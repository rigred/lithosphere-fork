# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""
from __future__ import with_statement
from contextlib import nested
from json import dump, load
import os, sys, os

from ctypes import string_at
import pyglet
import pyglet.gl
from pyglet.gl import *
from pyglet.clock import ClockDisplay

from halogen import Root, Area, Workspace, here, Button, FileOpen, FileSave, res_open, res_listdir
from gletools import Texture, Framebuffer, ShaderProgram, FragmentShader, Viewport, Screen, Sampler2D

from .toolbar import Toolbar
from .terrain import Terrain
from .lines import LineCanvas
from .viewport import View3d
from .node_factory import NodeFactory
from .util import quad

class Application(object):
    def __init__(self, window):
        self.window = window
        window.set_fullscreen(True)

        self.fps = ClockDisplay()
        self.mesh_width = 512
        self.mesh_height = 512

        self.width = 1024
        self.height = 1024
        self.shaders = {}

        self.framebuffer = Framebuffer()
        self.window.push_handlers(self)
        
        font_dir = here('style/fonts')
        for name in res_listdir(here('style/fonts')):
            font_path = os.path.join(font_dir, name)
            pyglet.font.add_file(res_open(font_path))
        
        self.root = Root(self.window, here('style/style.hss'))

        self.file_open = FileOpen(self.root, pattern=r'.*\.lth$')
        self.file_open.on_file = self.open
        
        self.file_save = FileSave(self.root, pattern=r'.*\.lth$')
        self.file_save.on_file = self.save

        self.export_png_dialog = FileSave(self.root, pattern=r'.*\.png$')
        self.export_png_dialog.on_file = self.export_png

        self.work_area = Area(id='sidebar').append_to(self.root)
        self.workspace = Workspace().append_to(self.work_area)
        self.canvas = LineCanvas().append_to(self.workspace)
        self.processing_view = Screen(0, 0, self.width, self.height)
        self.terrain = Terrain(self)
        
        self.export_obj_dialog = FileSave(self.root, pattern=r'.*\.obj$')
        self.export_obj_dialog.on_file = self.terrain.export_obj
        
        self.export_heights_dialog = FileSave(self.root, pattern=r'.*\.farr$')
        self.export_heights_dialog.on_file = self.terrain.export_float_array

        self.viewport = View3d(self).append_to(self.root)
        self.toolbar = Toolbar(self)
        self.node_factory = NodeFactory(self)
        pyglet.clock.schedule_interval(self.update, 0.05)
        pyglet.clock.schedule(lambda delta: None) #DEBUG
        self.temp = self.create_texture()
        self.height_reset = self.shader('height_reset.frag')

        self.nodes = []
        self.export_target = Texture(self.width, self.height, format=GL_RGB)

    def export_png(self, filename):
        if not filename.endswith('.png'):
            filename += '.png'
        source = self.terrain.material.source
        if source:
            source.texture.unit = GL_TEXTURE0
            self.framebuffer.textures[0] = self.export_target
            glColor4f(1.0, 1.0, 1.0, 1.0)
            with nested(self.processing_view, source.texture, self.framebuffer):
                quad(self.width, self.height)
            glFinish()
            self.export_target.save(filename)

    def add_node(self, node):
        self.nodes.append(node)

    def remove_node(self, node):
        self.nodes.remove(node)

    def open(self, filename):
        with open(filename) as file:
            data = load(file)

        self.empty()

        instances = dict()
        nodes_data = dict()
        for id, node_data in data['nodes'].items():
            instance = self.node_factory.create(node_data)
            instance.id = id
            instances[id] = instance
            nodes_data[id] = node_data

        for id, instance in instances.items():
            node_data = nodes_data[id]
            instance.reconnect(node_data['sources'], instances)

        self.terrain.open(data['terrain'], instances)
        
        workspace_off = data['workspace']['offset']
        self.workspace.xoff, self.workspace.yoff = workspace_off['x'], workspace_off['y']
        
        self.viewport.pos.xyz = data['viewport']['position']
        self.viewport.rotation.xyz = data['viewport']['rotation']

    def save(self, filename):
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
            nodes[node.id] = dict(
                type = node.__class__.__name__,
                offset = dict(x=node.widget.rect.x, y=node.widget.rect.y),
                parameters = node.parameters,
                sources = dict(
                    (name, (slot.source.id if slot.source else None))
                    for name, slot in node.sources.items()
                )
            )

        terrain = self.terrain
        data['terrain'] = dict(
            offset = dict(x=terrain.widget.rect.x, y = terrain.widget.rect.y),
            input_height = terrain.input_height.source.id if terrain.input_height.source else None,
            material = terrain.material.source.id if terrain.material.source else None,
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
        glClearColor(0.3, 0.3, 0.3, 1.0)
        self.window.clear()
        self.viewport.draw_terrain()
        self.root.draw()
        #self.fps.draw()

    def create_texture(self):
        return Texture(self.width, self.height, format=GL_RGBA32F, clamp='st')

    def shader(self, *names, **kwargs):
        if names in self.shaders:
            return self.shaders[names]
        else:
            shader = ShaderProgram(*[
                FragmentShader.open(res_open(here('shaders/%s' % name)))
                if name.endswith('.frag') else
                VertexShader.open(res_open(here('shaders/%s' % name)))
                for name in names
            ], **kwargs)
            self.shaders[names] = shader
            return shader

    def update(self, delta):
        self.terrain.update()
