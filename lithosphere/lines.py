from pyglet.gl import *
from halogen import Canvas

class LineCanvas(Canvas):
    def __init__(self):
        Canvas.__init__(self, id='canvas')
        self.outputs = []
        
    def on_draw(self):
        glLineWidth(3.0)
        glTexCoord2f(
            self.root.resources.white.left,
            self.root.resources.white.bottom,
        )
        glColor4f(255.0/255.0, 184.0/255.0, 48.0/255.0, 0.7)
        glBegin(GL_LINES)
        for output in self.outputs:
            start = output.rect.center
            end = output.connector.rect.center
            glVertex3f(start.x, start.y, 0)
            glVertex3f(end.x, end.y, 0)
        glEnd()

    def add(self, output):
        self.outputs.append(output)

