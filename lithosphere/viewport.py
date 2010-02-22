# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""
from halogen import Node, here
from gletools import Projection, ShaderProgram, VertexShader, FragmentShader, DepthTest
from pyglet.gl import *
from pyglet.window.key import S, D, F, E, W, R, LSHIFT

from .util import nested
from .math3d import Vector, Matrix

def hex2color(hex):
    return (
        int(hex[:2], 16)/255.0,
        int(hex[2:4], 16)/255.0,
        int(hex[4:], 16)/255.0,
    )

class View3d(Node):
    def __init__(self, application):
        Node.__init__(self)
        self.application = application

        self.sun = ShaderProgram(
            VertexShader.open(here('shaders/lighting/default.vert')),
            FragmentShader.open(here('shaders/lighting/sun.frag')),
            color = (1.0, 1.0, 1.0),
            direction = (-0.5, -0.5, 0.2),
            ambient = (0.1, 0.1, 0.1),
        )

        self.hemisphere = self.load_lighting('hemisphere.frag',
            ground_color = hex2color('4e4a3e'),
            sky_color = hex2color('e4f5fb'),
            direction = (-0.5, -0.5, 0.2),
            ambient = (0.2, 0.2, 0.2),
        )

        self.spherical_harmonics = self.load_lighting('spherical_harmonics.frag')
        
        self.light = self.spherical_harmonics
        
        self.speed = Vector(0, 0, 0)
        self.angular_speed = Vector(0, 0, 0)

        self.pos = Vector(-0.957, 0.690, -0.372)
        self.rotation = Vector(1.218, 0.000, 0.680)

        self.matrix = Matrix()
        self.at = self.matrix * Vector(0, 0, 1)
        self.up = self.matrix * Vector(0, 1, 0)

        pyglet.clock.schedule_interval(self.update_view, 0.03)
        self.factor = 0.10
    
    def load_lighting(self, name, **kwargs):
        return ShaderProgram(
            VertexShader.open(here('shaders/lighting/default.vert')),
            FragmentShader.open(here('shaders/lighting/%s' % name)),
            **kwargs
        )
        

    def update_view(self, delta):
        self.dampen()

        if self.state.focus:
            leftright = self.getaxis(F, S)
            updown = self.getaxis(W, R)
            frontback = self.getaxis(D, E)
            self.speed += (self.matrix * Vector(leftright, updown, frontback)) * delta * self.factor

        self.pos += self.speed
        if self.pos.length > 2.0:
            self.pos.scale(2.0)

        self.rotation += self.angular_speed
        if self.rotation.z > 1.3:
            self.rotation.z  = 1.3
        elif self.rotation.z < -1.3:
            self.rotation.z = -1.3

        self.matrix.rotate(self.rotation)
        self.at = self.matrix * Vector(0, 0, 1)
        self.up = self.matrix * Vector(0, 1, 0)

    def dampen(self):
        self.speed *= 0.9 
        self.angular_speed *= 0.75

    def getaxis(self, key1, key2):
        value = 0.0
        factor = 0.2 if self.root.keys[LSHIFT] else 1.0
        if self.root.keys[key1]:
            value -= factor
        if self.root.keys[key2]:
            value += factor
        return value
    
    def draw_terrain(self):
        rect = self.rect
        with nested(
            Projection(rect.left, rect.bottom, rect.width, rect.height, fov=40, near=0.001, far=4.0), 
            self.light,
            DepthTest,
        ):
            glPushMatrix() 
            glLoadIdentity()
            gluLookAt(
                self.pos.x, self.pos.y, self.pos.z,
                self.pos.x + self.at.x, self.pos.y + self.at.y, self.pos.z + self.at.z,
                self.up.x, self.up.y, self.up.z,
            )
            glColor4f(0.5, 0.5, 0.5, 1.0)
            self.application.terrain.draw()
            self.draw_unit_cube()
            glPopMatrix()

    def draw_unit_cube(self):
        glPushMatrix()
        glLineWidth(1.0)
        glEnable(GL_BLEND)
        glColor4f(0.4, 0.4, 0.4, 0.1)
        glTranslatef(0.0, 0.5, 0.0)
        pyglet.graphics.draw(24, GL_LINES, ('v3f', (
            +0.5, +0.5, +0.5, -0.5, +0.5, +0.5,
            -0.5, +0.5, +0.5, -0.5, +0.5, -0.5,
            -0.5, +0.5, -0.5, +0.5, +0.5, -0.5,
            +0.5, +0.5, -0.5, +0.5, +0.5, +0.5,
            
            +0.5, -0.5, +0.5, -0.5, -0.5, +0.5,
            -0.5, -0.5, +0.5, -0.5, -0.5, -0.5,
            -0.5, -0.5, -0.5, +0.5, -0.5, -0.5,
            +0.5, -0.5, -0.5, +0.5, -0.5, +0.5,
            
            +0.5, +0.5, +0.5, +0.5, -0.5, +0.5,
            -0.5, +0.5, +0.5, -0.5, -0.5, +0.5,
            -0.5, +0.5, -0.5, -0.5, -0.5, -0.5,
            +0.5, +0.5, -0.5, +0.5, -0.5, -0.5,
        )))
        glDisable(GL_BLEND)
        glPopMatrix()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.angular_speed += Vector(-dx*self.factor*0.003, 0, -dy*self.factor*0.003)

    def on_mouse_press(self, x, y, button, modifiers):
        self.mousepos = x, y
        self.root.window.set_exclusive_mouse(True)
        self.root.window.push_handlers(
            on_mouse_release    = self.on_mouse_release,
            on_mouse_drag       = self.on_mouse_drag,
        )

    def on_mouse_release(self, x, y, button, modifiers):
        self.root.window.set_mouse_position(*self.mousepos)
        self.root.window.set_exclusive_mouse(False)
        self.root.window.remove_handlers(
            on_mouse_release    = self.on_mouse_release,
            on_mouse_drag       = self.on_mouse_drag,
        )
