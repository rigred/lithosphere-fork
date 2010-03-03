# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""
from __future__ import with_statement

from pyglet.gl import *
from halogen import Widget, Column, Label, Button, Area
from .util import Output, LabelSlider, quad, nested

class Node(object):
    def __init__(self, label, application):
        self.application = application
        application.add_node(self)
        self.column = Column()
        bar_area = Area().add_class('widget_bar')
        Label(label).append_to(bar_area)
        Button().append_to(bar_area).on_click = self.delete
        self.texture = application.create_texture()
        self.widget = Widget(bar_area, self.column).add_class('node').append_to(application.workspace)

    def get_parameters(self):
        return []
    def set_parameters(self, values):
        pass
    parameters = property(get_parameters, set_parameters)
    del get_parameters, set_parameters

    @property
    def sources(self):
        return dict()

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

    def reconnect(self, data, instances):
        pass
    
    def apply(self, shader, target, *sources):
        view = self.application.processing_view
        
        for i, source in enumerate(sources):
            source.unit = GL_TEXTURE0 + i

        fbo = self.application.framebuffer
        fbo.textures[0] = target

        with nested(view, fbo, shader, *sources):
            quad(target.width, target.height)
