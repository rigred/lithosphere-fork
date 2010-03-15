# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""
from __future__ import with_statement
import os

from pyglet.gl import *
from halogen import Widget, Column, Label, Button, Area
from .util import Output, LabelSlider, quad, nested, connect

class Node(object):
    def __init__(self, label, application):
        self.application = application
        self.id = os.urandom(16).encode('hex')

        application.add_node(self)
        self.column = Column()
        bar_area = Area().add_class('widget_bar')
        Label(label).append_to(bar_area)
        Button().append_to(bar_area).on_click = self.delete
        self.texture = application.create_texture()
        self.widget = Widget(bar_area, self.column).add_class('node').append_to(application.workspace)
        self._parameters = {}
        self.sources = {}
        self.updated = None
        self.optional = []
    
    @property
    def revision(self):
        sources = tuple([input.source.revision if input.source else None for input in self.sources.values()])
        parameters = tuple((name, param.value) for name, param in self._parameters.items())
        return hash((self.__class__.__name__, parameters, sources))
    
    def get_parameters(self):
        return dict((name, param.value) for name, param in self._parameters.items())
    def set_parameters(self, values):
        for name, value in values.items():
            self._parameters[name].value = value

    parameters = property(get_parameters, set_parameters)
    del get_parameters, set_parameters

    def update_sources(self):
        for input in self.sources.values():
            if input.source:
                input.source.update()

    @property
    def complete(self):
        for name, input in self.sources.items():
            if name in self.optional:
                continue
            else:
                if input.source and input.source.complete:
                    continue 
                else:
                    return False

        return True

    def update(self):
        if self.complete:
            revision = self.revision
            self.update_sources()
            if revision != self.updated:
                self.compute()
            self.updated = revision 
    
    def reconnect(self, data, instances):
        for name, id in data.items():
            if id:
                instance = instances[id]
                input = self.sources[name]
                connect(instance, input)

    def delete(self):
        self.output.delete()
        self.texture.delete()
        for name, slot in self.sources.items():
            if slot.content:
                slot.content.delete()
                slot.content = None
            if slot.source:
                slot.source = None
        self.widget.remove()
        self.application.remove_node(self)
    
    def apply(self, shader, target, *sources):
        view = self.application.processing_view
        
        for i, source in enumerate(sources):
            source.unit = GL_TEXTURE0 + i

        fbo = self.application.framebuffer
        fbo.textures[0] = target

        with nested(view, fbo, shader, *sources):
            quad(target.width, target.height)
