from halogen import Widget
from .util import Input, nested, quad, connect
from gletools import Texture, Framebuffer, VertexObject
from pyglet.gl import *
from ctypes import c_float, c_uint

class Terrain(object):
    def __init__(self, application):
        self.application = application
        self.input = Input(self)
        self.width, self.height = width, height = application.mesh_width, application.mesh_height
        self.widget = Widget('Terrain', self.input, id='terrain').append_to(application.workspace)
        
        self.vertex_texture = Texture(width, height, GL_RGBA32F)
        self.normal_texture = Texture(application.width, application.height, GL_RGBA32F)

        self.vertex_fbo = Framebuffer(
            self.vertex_texture,
        )
        self.normal_fbo = Framebuffer(
            self.normal_texture,
        )

        self.update_vertex_shader = application.shader('update_vertex.frag')
        self.update_normals_shader = application.shader('update_normals.frag')
        self.update_normals_shader.vars.offsets = 1.0/application.width, 1.0/application.height

        self.reset_vertex = application.shader('reset_vertex.frag')
        self.reset_normals = application.shader('reset_normals.frag')
        self.vbo = self.generate_vbo(width, height)

        self.reset()
        self.updated = True

    def generate_vbo(self, width, height):
        #as an acceleration the arrays could be prefilled in C

        v4f = (c_float*(width*height*4))()
        width_factor, height_factor = 1.0/float(width), 1.0/float(height)
        for z in range(height):
            for x in range(width):
                offset = (x+z*width)*4
                v4f[offset:offset+4] = x*width_factor, 0, z*height_factor, 1

        at = lambda x, y: x+y*width
        
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
        input_id = data['source']
        if input_id:
            node = instances[input_id]
            connect(node, self.input)

    def reset(self):
        view = self.application.processing_view
        with nested(view, self.vertex_fbo, self.reset_vertex):
            quad(self.width, self.height)
            self.vbo.vertices.copy_from(self.vertex_texture)
        with nested(view, self.normal_fbo, self.reset_normals):
            quad(self.application.width, self.application.height)

    def update(self):
        view = self.application.processing_view
        revision = self.revision
        if self.input.source:
            self.input.source.update()
            if revision != self.updated:
                with nested(view, self.vertex_fbo, self.input.source.texture, self.update_vertex_shader):
                    quad(self.width, self.height)
                    self.vbo.vertices.copy_from(self.vertex_texture)

                with nested(view, self.normal_fbo, self.input.source.texture, self.update_normals_shader):
                    quad(self.application.width, self.application.height)
        else:
            if revision != self.updated:
                self.reset()

        self.updated = revision

    @property
    def revision(self):
        if self.input.source:
            return self.input.source.revision
        else:
            return None
    
    def draw(self):
        glPushMatrix()
        glTranslatef(-0.5, 0, -0.5)
        with self.normal_texture:
            self.vbo.draw(GL_TRIANGLES)
        glPopMatrix()
