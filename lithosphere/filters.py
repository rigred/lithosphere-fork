# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from halogen import Widget, Column, Area
from gletools import Sampler2D

from .util import Output, Input, quad, nested, slider
from pyglet.gl import *

class Gaussian(object):
    def __init__(self, application):
        self.application = application
        self.texture = application.create_texture()
        column = Column()
        self.inout = Area().append_to(column).add_class('inout')
        self.input = Input(self).append_to(self.inout)
        self.output = Output(self).append_to(self.inout)
        self.widget = Widget('Gaussian', column).add_class('node').append_to(application.workspace)
        
        self.shader_x = application.shader('gaussian_x.frag')
        self.shader_x.vars.texture = Sampler2D(GL_TEXTURE0)
        self.shader_x.vars.offsets = 1.0/self.texture.width, 1.0/self.texture.height
        
        self.shader_y = application.shader('gaussian_y.frag')
        self.shader_y.vars.texture = Sampler2D(GL_TEXTURE0)
        self.shader_y.vars.offsets = 1.0/self.texture.width, 1.0/self.texture.height

        self.updated = False
        self.slider('Repeat', 'repeat', 0.01)
    
    def slider(self, title, name, initial):
        setattr(self, name, initial)
        def on_change(value):
            setattr(self, name, value)
        slider(title, on_change, initial).insert_before(self.inout)

    def update(self):
        if self.input.source:
            self.input.source.update()
            revision = self.revision

            if revision != self.updated:
                input = self.input.source.texture
                input.unit = GL_TEXTURE0
                output = self.texture
                output.unit = GL_TEXTURE0
                temp = self.application.temp
                temp.unit = GL_TEXTURE0

                fbo = self.application.framebuffer
                fbo.textures[0] = temp
                with nested(fbo, self.shader_x, input):
                    quad(output.width, output.height)
                
                fbo.textures[0] = output
                with nested(fbo, self.shader_y, temp):
                    quad(output.width, output.height)

                for i in range(int(self.repeat*100.0)):
                    fbo.textures[0] = temp
                    with nested(fbo, self.shader_x, output):
                        quad(output.width, output.height)
                    
                    fbo.textures[0] = output
                    with nested(fbo, self.shader_y, temp):
                        quad(output.width, output.height)

                self.updated = revision
                return True
    
    @property
    def revision(self):
        if self.input.source:
            return hash((self.__class__.__name__, self.repeat, self.input.source.revision))
        else:
            return hash((self.__class__.__name__, self.repeat))

class Erode(object):
    def __init__(self, application):
        self.application = application
        self.texture = application.create_texture()
        column = Column()
        self.inout = Area().append_to(column).add_class('inout')
        self.input = Input(self).append_to(self.inout)
        self.output = Output(self).append_to(self.inout)
        self.widget = Widget('Erode', column).add_class('node').append_to(application.workspace)
        
        self.shader = application.shader('erode.frag')
        self.shader.vars.texture = Sampler2D(GL_TEXTURE0)
        self.shader.vars.offsets = 1.0/self.texture.width, 1.0/self.texture.height
        
        self.updated = False
        self.slider('Repeat', 'repeat', 0.0)
    
    def slider(self, title, name, initial):
        setattr(self, name, initial)
        def on_change(value):
            setattr(self, name, value)
        slider(title, on_change, initial).insert_before(self.inout)

    def update(self):
        if self.input.source:
            self.input.source.update()
            revision = self.revision

            if revision != self.updated:
                input = self.input.source.texture
                input.unit = GL_TEXTURE0
                output = self.texture
                output.unit = GL_TEXTURE0
                temp = self.application.temp
                temp.unit = GL_TEXTURE0
                self.shader.vars.invert = False

                fbo = self.application.framebuffer
                fbo.textures[0] = output
                with nested(fbo, self.shader, input):
                    quad(output.width, output.height)
            
                for i in range(int(self.repeat*100.0)):
                    fbo.textures[0] = temp
                    with nested(fbo, self.shader, output):
                        quad(output.width, output.height)
                    
                    fbo.textures[0] = output
                    with nested(fbo, self.shader, temp):
                        quad(output.width, output.height)

                self.updated = revision
                return True
    
    @property
    def revision(self):
        if self.input.source:
            return hash((self.__class__.__name__, self.repeat, self.input.source.revision))
        else:
            return hash((self.__class__.__name__, self.repeat))
