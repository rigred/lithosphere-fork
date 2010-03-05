# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from pyglet.gl import *
from halogen import Canvas

class LineCanvas(Canvas):
    def __init__(self):
        Canvas.__init__(self, id='canvas')
        self.connectors = []
        
    def on_draw(self):
        glLineWidth(3.0)
        glTexCoord2f(
            self.root.resources.white.left,
            self.root.resources.white.bottom,
        )
        glColor4f(255.0/255.0, 184.0/255.0, 48.0/255.0, 0.7)
        glBegin(GL_LINES)
        for connector in self.connectors:
            start = connector.output.rect.center
            end = connector.rect.center
            glVertex3f(start.x, start.y, 0)
            glVertex3f(end.x, end.y, 0)
        glEnd()

    def add(self, connector):
        self.connectors.append(connector)

    def remove(self, connector):
        self.connectors.remove(connector)

