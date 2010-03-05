# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from pyglet.event import EventDispatcher
from UniversalDialogs import AskFileForOpen, AskFileForSave

class Dialogs(EventDispatcher):
    def open(self):
        filename = AskFileForOpen(windowTitle='Choose a terrain to open', typeList=['*.lth'])
        if filename:
            self.dispatch_event('on_open', filename)

    def save(self):
        filename = AskFileForSave(windowTitle='Save', fileType=['*.lth'])
        if filename:
            self.dispatch_event('on_save', filename)

Dialogs.register_event_type('on_open')
Dialogs.register_event_type('on_save')
