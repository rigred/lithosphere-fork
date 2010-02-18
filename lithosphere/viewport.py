# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""
from halogen import Node, here
from gletools import Projection, ShaderProgram, VertexShader, FragmentShader, DepthTest
from pyglet.gl import *
from pyglet.window.key import S, D, F, E, W, R

from .util import nested
from .math3d import Vector, Matrix

class Viewport(Node):
    def __init__(self, application):
        Node.__init__(self)
        self.application = application
        self.sun = ShaderProgram(
            VertexShader.open(here('shaders/sun.vert')),
            FragmentShader.open(here('shaders/sun.frag')),
            color = (1.0, 1.0, 1.0),
            direction = (-0.5, -0.5, 0.2),
            ambient = (0.1, 0.1, 0.1),
        )
        
        self.speed = Vector(0, 0, 0)
        self.angular_speed = Vector(0, 0, 0)

        self.pos = Vector(-0.559, 0.615, -0.128)
        self.rotation = Vector(1.031, 0.000, 0.440)

        self.matrix = Matrix()
        self.at = self.matrix * Vector(0, 0, 1)
        self.up = self.matrix * Vector(0, 1, 0)

        pyglet.clock.schedule_interval(self.update_view, 0.03)
        self.factor = 0.10

    def update_view(self, delta):
        self.dampen()

        if self.state.focus:
            leftright = self.getaxis(F, S)
            updown = self.getaxis(W, R)
            frontback = self.getaxis(D, E)
            self.speed += (self.matrix * Vector(leftright, updown, frontback)) * delta * self.factor

        self.pos += self.speed
        self.rotation += self.angular_speed
        self.matrix.rotate(self.rotation)
        self.at = self.matrix * Vector(0, 0, 1)
        self.up = self.matrix * Vector(0, 1, 0)

    def dampen(self):
        self.speed *= 0.9 
        self.angular_speed *= 0.75

    def getaxis(self, key1, key2):
        value = 0.0
        if self.root.keys[key1]:
            value -= 1.0
        if self.root.keys[key2]:
            value += 1.0
        return value
    
    def draw_terrain(self):
        rect = self.rect
        with nested(
            Projection(rect.left, rect.bottom, rect.width, rect.height, fov=40, near=0.01), 
            self.sun,
            DepthTest,
        ):
            glPushMatrix() 
            glLoadIdentity()
            gluLookAt(
                self.pos.x, self.pos.y, self.pos.z,
                self.pos.x + self.at.x, self.pos.y + self.at.y, self.pos.z + self.at.z,
                self.up.x, self.up.y, self.up.z,
            )
            glColor3f(0.7, 0.7, 0.7)
            self.application.terrain.draw()
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
