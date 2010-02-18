# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from halogen import Widget, Column

from .util import Output, slider, quad, nested

class Source(object):
    def __init__(self, label, application, shader):
        self.application = application
        self.texture = application.create_texture()
        column = Column()
        self.output = Output(self).append_to(column)
        self.widget = Widget(label, column).append_to(application.work_area)
        self.vars = dict()
        self.shader = application.shader(shader)
        self.dirty = True

    def slider(self, title, name, initial, scale=1.0):
        self.vars[name] = initial * scale
        def on_change(value):
            self.vars[name] = value * scale
            self.dirty = True
        slider(title, on_change, initial).insert_before(self.output)

    def update(self):
        if self.dirty:
            for name, value in self.vars.items():
                self.shader.vars[name] = value
            
            fbo = self.application.framebuffer
            fbo.textures[0] = self.texture
            with nested(fbo, self.shader):
                quad(self.texture.width, self.texture.height)

            self.dirty = False
            return True
        else:
            return False

class Random(Source):
    def __init__(self, application):
        Source.__init__(self, 'Random', application, 'random.frag') 
        self.slider('Seed', 'seed', 0.8)
        self.slider('Height', 'height', 0.2)

class Simplex(Source):
    def __init__(self, application):
        Source.__init__(self, 'Simplex', application, 'simplex.frag') 
        self.slider('Size', 'size', 0.02, 255.0)
        self.slider('Height', 'height', 0.1)
        self.slider('Offset', 'offset', 0.0, 100.0)
