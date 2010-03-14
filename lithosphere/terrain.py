# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""
from __future__ import with_statement

from halogen import Widget, Column
from .util import LabelInput, nested, quad, connect
from gletools import Texture, Framebuffer, VertexObject
from pyglet.gl import *
from ctypes import c_float, c_uint

class Terrain(object):
    id = 'terrain'

    def __init__(self, application):
        self.application = application
        self.width, self.height = width, height = application.mesh_width, application.mesh_height
       
        col = Column() 
        self.input_height = LabelInput('Height', self).append_to(col).input
        self.material = LabelInput('Material', self).append_to(col).input
        
        self.widget = Widget('Terrain', col, id='terrain').append_to(application.workspace)

        self.default_material = Texture(2, 2, GL_RGBA, data=(140, 140, 140, 255)*4)
        self.vertex_texture = Texture(width, height, GL_RGBA32F)
        self.normal_texture = Texture(application.width, application.height, GL_RGBA32F, unit=GL_TEXTURE0)

        self.vertex_fbo = Framebuffer(self.vertex_texture)
        self.normal_fbo = Framebuffer(self.normal_texture)

        self.update_vertex_shader = application.shader('update_vertex.frag')
        self.update_normals_shader = application.shader('update_normals.frag')
        self.update_normals_shader.vars.offsets = 1.0/application.width, 1.0/application.height

        self.reset_vertex = application.shader('reset_vertex.frag')
        self.reset_normals = application.shader('reset_normals.frag')
        self.vbo = self.generate_vbo(width, height)

        self.reset()
        self.updated = None

    def export_obj(self, filename):
        if not filename.endswith('.obj'):
            filename += '.obj'

        if self.input_height.source:
            heightmap = self.input_height.source.texture
            heightmap.retrieve()

            width, height = self.application.width, self.application.height

            with open(filename, 'w') as outfile:
                heights = map(lambda z: (z, float(z)/height), range(height))
                widths = map(lambda x: (x, float(x)/width), range(width))
                for iz, z in heights:
                    for ix, x in widths:
                        outfile.write('v %f %f %f\n' % (x, heightmap[ix, iz][0], z))
                '''
                self.vertex_texture.retrieve()
                for vertex in self.vertex_texture:
                    outfile.write('v %f %f %f\n' % tuple(vertex[:3]))
                '''

                self.normal_texture.retrieve()
                for normal in self.normal_texture:
                    outfile.write('vn %f %f %f\n' % tuple(normal[:3]))

                heights = map(lambda x: float(x)/height, range(height))
                widths = map(lambda y: float(y)/width, range(width))
                for y in heights:
                    for x in widths:
                        outfile.write('vt %f %f\n' % (x, y))
            
                i_width, i_height = width-1, height-1
                for z in range(i_height):
                    for x in range(i_width):
                        offset = (x+z*i_width)*6
                        p1 = x+z*width
                        p2 = p1+width
                        p4 = p1+1
                        p3 = p2+1
                        outfile.write('f %i/%i/%i %i/%i/%i %i/%i/%i\n' % (
                            p1, p1, p1, p2, p2, p2, p3, p3, p3
                        ))
                        outfile.write('f %i/%i/%i %i/%i/%i %i/%i/%i\n' % (
                            p1, p1, p1, p3, p3, p3, p4, p4, p4
                        ))

    def generate_vbo(self, width, height):
        #as an acceleration the arrays could be prefilled in C

        v4f = (c_float*(width*height*4))()
        width_factor, height_factor = 1.0/float(width), 1.0/float(height)
        for z in range(height):
            for x in range(width):
                offset = (x+z*width)*4
                v4f[offset:offset+4] = x*width_factor, 0, z*height_factor, 1

        i_width, i_height = width-1, height-1
        indices = (c_uint*(i_width*i_height*6))()
        for z in range(i_height):
            for x in range(i_width):
                offset = (x+z*i_width)*6
                p1 = x+z*width
                p2 = p1+width
                p4 = p1+1
                p3 = p2+1
                indices[offset:offset+6] = p1, p2, p3, p1, p3, p4

        return VertexObject(
            pbo                 = True,
            indices             = indices,
            dynamic_draw_v4f    = v4f,
        )

    def open(self, data, instances):
        offset = data['offset']
        self.widget.rect.x, self.widget.rect.y = offset['x'], offset['y']
        self.widget.layout()

        input_id = data['input_height']
        if input_id:
            node = instances[input_id]
            connect(node, self.input_height)
        
        material_id = data['material']
        if material_id:
            node = instances[material_id]
            connect(node, self.material)

    def reset(self):
        view = self.application.processing_view
        self.vertex_fbo.textures[0] = self.vertex_texture
        with nested(view, self.vertex_fbo, self.reset_vertex):
            quad(self.width, self.height)
            self.vbo.vertices.copy_from(self.vertex_texture)
        with nested(view, self.normal_fbo, self.reset_normals):
            quad(self.application.width, self.application.height)

    def update(self):
        view = self.application.processing_view
        revision = self.revision

        if self.material.source:
            self.material.source.update()

        if self.input_height.source:
            self.input_height.source.update()

        if revision != self.updated:
            if self.input_height.source:
                source = self.input_height.source.texture
                source.unit = GL_TEXTURE0
                
                self.vertex_fbo.textures[0] = self.vertex_texture
                with nested(view, self.vertex_fbo, source, self.update_vertex_shader):
                    quad(self.width, self.height)
                    self.vbo.vertices.copy_from(self.vertex_texture)

                with nested(view, self.normal_fbo, source, self.update_normals_shader):
                    quad(self.application.width, self.application.height)
            else:
                self.reset()

        self.updated = revision

    @property
    def revision(self):
        if self.input_height.source:
            height = self.input_height.source.revision
        else:
            height = None

        if self.material.source:
            material = self.material.source.revision
        else:
            material = None

        return hash((height, material))
    
    def draw(self):
        glPushMatrix()
        glTranslatef(-0.5, 0, -0.5)
        self.normal_texture.unit = GL_TEXTURE0

        if self.material.source:
            self.material.source.texture.unit = GL_TEXTURE1
            with nested(self.normal_texture, self.material.source.texture):
                self.vbo.draw(GL_TRIANGLES)
        else:
            self.default_material.unit = GL_TEXTURE1
            with nested(self.normal_texture, self.default_material):
                self.vbo.draw(GL_TRIANGLES)
        glPopMatrix()
