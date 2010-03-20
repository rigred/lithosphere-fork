import sys, os, traceback
from pyglet.gl import *
import pyglet
from halogen import Root, here, res_open, res_listdir, Label, Widget, Column, Button

message = ''
run = True

def check(msg, required, version, plain_version):
    global message, run
    if version < required:
        run = False
        message += msg + ' you have: ' + plain_version + '\n'

def check_python():
    version = sys.version_info[0] * 10 + sys.version_info[1]
    plain = 'python %s.%s' % (sys.version_info[0], sys.version_info[1])
    check('- python 2.6 is required.', 26, version, plain)

def check_glsl():
    plain = string_at(glGetString(GL_SHADING_LANGUAGE_VERSION)).split(' ')[0]
    major, minor = map(int, plain.split('.'))
    version = major*100 + minor
    check('- glsl 1.30 is required.', 130, version, 'glsl ' + plain)

def check_extension(name):
    global message, run
    if not gl_info.have_extension('GL_ARB_' + name):
        if not gl_info.have_extension('GL_EXT_' + name):
            message += '- opengl extension %s not available\n' % name
            run = False

def check_extensions():
    check_extension('texture_float')
    check_extension('pixel_buffer_object')
    check_extension('vertex_buffer_object')
    check_extension('framebuffer_object')

def check_compatibility():
    check_python() 
    check_glsl()
    check_extensions()

class InfoApp(object):
    def __init__(self, window):
        self.window = window
        window.set_fullscreen(False)

        font_dir = here('style/fonts')
        window.push_handlers(self.on_draw)
        for name in res_listdir(here('style/fonts')):
            font_path = os.path.join(font_dir, name)
            pyglet.font.add_file(res_open(font_path))
        
        self.root = Root(window, here('style/style.hss'))
    
    def run(self):
        pyglet.app.run()

    def on_draw(self):
        glClearColor(0.3, 0.3, 0.3, 1.0)
        self.window.clear()
        self.root.draw()

    def message(self, title, text):
        col = Column()
        Label(text).append_to(col)
        Button('Close').append_to(col).on_click = self.exit
        Widget(title, col, dragable=False).append_to(self.root).add_class('message')

    def exit(self):
        sys.exit(0)

def main():
    window = pyglet.window.Window(fullscreen=False, resizable=True, vsync=False)

    check_compatibility()
    if run:
        try:
            from lithosphere.application import Application
            application = Application(window)
            if len(sys.argv) > 1:
                path = sys.argv[1]
                if os.path.exists(path):
                    application.open(path)
        except:
            traceback.print_exc()
            sys.exit(-1)
    else:
        application = InfoApp(window)
        application.message('Compatibility', message)
    application.run()
