# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""
from __future__ import with_statement

from euclid import Vector3
from random import random
from pyglet.graphics import vertex_list_indexed
from time import time

class Vertex(object):
    __slots__ = ['x', 'y', 'z', 'faces', 'index']
    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.faces = set()

    @property
    def normal(self):
        normal = Vertex(0, 0, 0)
        for face in self.faces:
            normal += face.normal
        return (normal/len(self.faces)).normalized

    def add_to_face(self, face):
        self.faces.add(face)

    def remove_from_face(self, face):
        self.faces.remove(face)

    def __iter__(self):
        return iter((self.x, self.y, self.z))

    def __sub__(self, other):
        return Vertex(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z,
        )
    def __add__(self, other):
        return Vertex(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z,
        )

    def __div__(self, scalar):
        scalar = float(scalar)
        return Vertex(
            self.x / scalar,
            self.y / scalar,
            self.z / scalar,
        )
    
    def __mul__(self, scalar):
        scalar = float(scalar)
        return Vertex(
            self.x * scalar,
            self.y * scalar,
            self.z * scalar,
        )

    @property
    def normalized(self):
        length = self.length
        return Vertex(
            self.x / length,
            self.y / length,
            self.z / length,
        )

    @property
    def length(self):
        return (self.x**2 + self.y**2 + self.z**2)**0.5

    def cross(self, other):
        return Vertex(
            self.y * other.z - self.z * other.y,
            -self.x * other.z + self.z * other.x,
            self.x * other.y - self.y * other.x
        )

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def __repr__(self):
        return '<Vertex %s %s %s>' % (self.x, self.y, self.z)

    @property
    def neighbors(self):        
        verts = set()
        for face in self.faces:
            v1, v2 = face.neighbors(self)
            verts.add(v1)
            verts.add(v2)
        return list(verts)

class Edge(object):
    __slots__ = ['v1', 'v2', '_hash']
    def __init__(self, v1, v2):
        self.v1, self.v2 = sorted((v1, v2))
        self._hash = hash((self.v1, self.v2))

    def subdivide(self):
        middle = self.v1+(self.v2-self.v1)/2.0
        faces  = list(self.v1.faces & self.v2.faces)
        for face in faces:
            face.insert_between(self.v1, self.v2, middle)

    def fractal_subdivide(self, scale=1.0):
        middle = self.v1+(self.v2-self.v1)/2.0
        length = middle.length
        range = abs(self.v1.length - self.v2.length) / 2.0
        rnd = random()*2.0-1.0
        length = length + rnd*range*scale
        middle.x, middle.y, middle.z = middle.normalized * length
        faces  = self.v1.faces & self.v2.faces
        for face in faces:
            face.insert_between(self.v1, self.v2, middle)

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return self.v1 == other.v1 and self.v2 == other.v2

class Face(object):
    __slots__ = ['verts', '_normal']
    def __init__(self, v1, v2, v3):
        v1.add_to_face(self)
        v2.add_to_face(self)
        v3.add_to_face(self)
        self.verts = [v1, v2, v3]
        self._normal = None

    def insert_between(self, v1, v2, middle):
        i1, i2 = self.verts.index(v1), self.verts.index(v2)
        i1, i2 = (i1, i2) if i1 < i2 else (i2, i1)
        if i1 == 0 and i2 == len(self.verts)-1:
            self.verts.append(middle)
        else:
            self.verts.insert(i2, middle)
        middle.add_to_face(self)

    def edges(self):
        for i in range(len(self.verts)-1):
            yield self.verts[i], self.verts[i+1]
        yield self.verts[-1], self.verts[0]

    def draw_lines(self):
        glBegin(GL_LINES)
        for v1, v2 in self.edges():
            glVertex3f(*v1)
            glVertex3f(*v2)
        glEnd()

    def draw_points(self):
        glPointSize(4.0)
        glBegin(GL_POINTS)
        for vertex in self.verts:
            glVertex3f(*vertex)
        glEnd()

    def draw_face(self):
        glNormal3f(*self.normal)
        glBegin(GL_TRIANGLES)
        for vertex in self.verts:
            glVertex3f(*vertex)
        glEnd()
    
    def tesselate(self):
        get = self.verts.__getitem__
        yield Face(get(0),get(1), get(5))
        yield Face(get(1),get(2), get(3))
        yield Face(get(3),get(4), get(5))
        yield Face(get(1),get(3), get(5))

    def neighbors(self, vertex):
        index = self.verts.index(vertex)
        if index == 0:
            return self.verts[-1], self.verts[1]
        elif index == len(self.verts)-1:
            return self.verts[1], self.verts[-2]
        else:
            return self.verts[index-1], self.verts[index+1]

    def unlink(self):
        for vertex in self.verts:
            vertex.remove_from_face(self)

    @property
    def normal(self):
        if self._normal is None:
            v1, v2, v3 = self.verts
            self._normal = (v2 - v1).cross(v3 - v1).normalized
        return self._normal

class Geometry(object):
    def __init__(self):
        phi = (1 + 5**0.5) / 2

        v1 = Vertex(1, phi, 0)
        v2 = Vertex(-1, phi, 0)
        v3 = Vertex(0, 1, phi)
        v4 = Vertex(0, 1, -phi)
        v5 = Vertex(phi, 0, 1)
        v6 = Vertex(-phi, 0, 1)
        v7 = Vertex(-phi, 0, -1)
        v8 = Vertex(phi, 0, -1)
        v9 = Vertex(0, -1, phi)
        v10 = Vertex(0, -1, -phi)
        v11 = Vertex(-1, -phi, 0)
        v12 = Vertex(1, -phi, 0)

        self.faces = [
            Face(v1, v2, v3),
            Face(v2, v1, v4),
            Face(v1, v3, v5),
            Face(v2, v6, v3),
            Face(v2, v7, v6),
            Face(v2, v4, v7),
            Face(v1, v5, v8),
            Face(v1, v8, v4),
            Face(v9, v3, v6),
            Face(v3, v9, v5),
            Face(v4, v10, v7),
            Face(v4, v8, v10),
            Face(v6, v7, v11),
            Face(v6, v11, v9),
            Face(v7, v10, v11),
            Face(v5, v12, v8),
            Face(v12, v5, v9),
            Face(v12, v10, v8),
            Face(v11, v12, v9),
            Face(v12, v11, v10),
        ]

        self.update()

        self.test()


    def test(self):
        print 'generating'
        start = time()
        self.subdivide()
        self.subdivide()
        self.subdivide()
        self.subdivide()
        self.spherize(2.5)
        self.randomize(0.03)
        self.fractal_subdivide()
        self.fractal_subdivide()
        self.fractal_subdivide()
        self.errode()
        self.errode()
        self.errode()
        self.accentuate()
        self.accentuate()
        self.fractal_subdivide()
        self.convolute(1.6, 0.9)
        print time() - start

    def asteroid(self):
        print 'generating'
        self.subdivide()
        self.spherize(2.0)
        self.randomize(0.3)
        self.smooth()
        self.fractal_subdivide(0.2)
        self.smooth()
        self.fractal_subdivide(0.2)
        self.smooth()
        self.fractal_subdivide(0.1)
        self.smooth()
        self.fractal_subdivide(0.05)
        self.smooth()
        self.smooth()
        self.fractal_subdivide(0.005)
        self.smooth()
        self.fractal_subdivide(0.002)
        print 'done'

    def planetoid(self):
        self.subdivide()
        self.subdivide()
        self.subdivide()
        self.spherize(2.5)
        self.randomize(0.05)
        self.fractal_subdivide(0.03)
        self.fractal_subdivide(0.01)
        self.fractal_subdivide(0.003)
        self.errode()
        self.errode()
        self.errode()
        self.errode()
        self.errode()
        self.accentuate()
        self.accentuate()
        self.accentuate()
        self.fractal_subdivide(0.001)

    def planet(self):
        self.subdivide()
        self.subdivide()
        self.subdivide()
        self.subdivide()
        self.spherize(2.5)
        self.fractal_subdivide(0.015)
        self.accentuate()
        self.fractal_subdivide(0.006)
        self.accentuate()
        self.errode()
        self.accentuate()
        self.errode()
        self.accentuate()
        self.errode()
        self.accentuate()
        self.errode()
        self.accentuate()
        self.fractal_subdivide(0.001)

    def update(self):
        self.calculate_edges()
        self.calculate_verts()

    def calculate_edges(self):
        edges = dict()

        for face in self.faces:
            for v1, v2 in face.edges():
                edge = Edge(v1, v2)
                edges[edge] = True        

        self.edges = edges.keys()

    def calculate_verts(self):
        self.verts = set()
        for face in self.faces:
            for vertex in face.verts:
                self.verts.add(vertex)

    def draw(self):
        for face in self.faces:
            face.draw_lines()

    def subdivide(self):
        for edge in self.edges:
            edge.subdivide()

        faces = self.faces
        self.faces = []
        for face in faces:
            for child in face.tesselate():
                self.faces.append(child)
            face.unlink()

        self.update()

    def fractal_subdivide(self, scale=1.0):
        for edge in self.edges:
            edge.fractal_subdivide(scale)
        
        faces = self.faces
        self.faces = []
        for face in faces:
            for child in face.tesselate():
                self.faces.append(child)
            face.unlink()

        self.update()

    def spherize(self, distance=1.0):
        for vertex in self.verts:
            vertex.x, vertex.y, vertex.z = vertex.normalized * distance

    def smooth(self):
        for vertex in self.verts:
            verts = set()
            for face in vertex.faces:
                v1, v2 = face.neighbors(vertex)
                verts.add(v1)
                verts.add(v2)
            verts.add(vertex)

            average_distance = 0
            for neighbor in verts:
                average_distance += neighbor.length
            average_distance /= len(verts)

            vertex.x, vertex.y, vertex.z = vertex.normalized * average_distance
    
    def errode(self):
        for vertex in self.verts:
            length = vertex.length
            average_distance = 0
            count = 0
            for neighbor in vertex.neighbors:
                neighbor_length = neighbor.length
                if neighbor_length <= length:
                    count += 1
                    average_distance += neighbor_length
            if count > 0:
                average_distance /= count
                vertex.x, vertex.y, vertex.z = vertex.normalized * average_distance
        
        for face in self.faces:
            face._normal = None

    def accentuate(self):
        for vertex in self.verts:
            length = vertex.length
            verts = set()
            for face in vertex.faces:
                v1, v2 = face.neighbors(vertex)
                verts.add(v1)
                verts.add(v2)
            verts.add(vertex)

            average_distance = 0
            count = 0
            for neighbor in verts:
                neighbor_length = neighbor.length
                count += 1
                average_distance += neighbor_length
            if count > 0:
                factor = 1.0 - vertex.normal.dot(vertex.normalized)
                average_distance /= count
                distance = length + (average_distance - length) * factor
                vertex.x, vertex.y, vertex.z = vertex.normalized * distance
        
        for face in self.faces:
            face._normal = None

    def randomize(self, factor=0.04):
        for vertex in self.verts:
            rnd = random() * 2 - 1
            off = 1.0 + rnd * factor
            vertex.x, vertex.y, vertex.z = vertex * off

    def convolute(self, center, periphery):
        for vertex in self.verts:
            length = vertex.length
            average = center * length
            neighbors = vertex.neighbors
            for neighbor in neighbors:
                average += periphery * neighbor.length
            average /= len(neighbors) + 1
            vertex.x, vertex.y, vertex.z = (vertex/length) * average

    def vertex_list(self):
        print 'vertex list'
        verts = list(self.verts)
        v3f = []
        n3f = []
        for i, vertex in enumerate(verts):
            vertex.index = i
            v3f.extend(vertex)
            n3f.extend(vertex.normal)
        indices = []
        for face in self.faces:
            for vertex in face.verts:
                indices.append(vertex.index)
        print 'done'
        return vertex_list_indexed(len(self.verts), indices,
            ('v3f', v3f),
            ('n3f', n3f),
        )

if __name__ == '__main__':
    import pyglet
    from pyglet.gl import *
    from gletools import Projection

    window = pyglet.window.Window(vsync=False, fullscreen=True)

    glEnable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glLightfv(GL_LIGHT0, GL_AMBIENT, (GLfloat*4)(0.1, 0.1, 0.1, 0.2))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (GLfloat*4)(0.3, 0.3, 0.3, 0.5))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (GLfloat*4)(0.2, 0.2, 0.2, 0.3))
    glLightfv(GL_LIGHT0, GL_POSITION, (GLfloat*4)(0, 0, 0, 1))

    rotation = 0.0

    geometry = Geometry()
    mesh = geometry.vertex_list()

    @window.event
    def on_draw():
        with Projection(0, 0, window.width, window.height, fov=65, near=0.1, far=20000):
            window.clear()
            glPushMatrix()
            glTranslatef(0, 0, -5)
            glRotatef(15, 1.0, 0.0, 0.0)
            glRotatef(rotation, 0.0, 1.0, 0.0)
            mesh.draw(GL_TRIANGLES)
            glPopMatrix()

    def simulate(delta):
        global rotation
        rotation += delta * 30
    pyglet.clock.schedule_interval(simulate, 0.03)

    pyglet.app.run()
