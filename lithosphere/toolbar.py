# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from halogen import Row, Button

class Toolbar(object):
    def __init__(self, application):
        self.application = application
        self.row = Row(id='toolbar').append_to(application.work_area)

    def add(self, type):
        button = Button(type.__name__).append_to(self.row)
        @button.event
        def on_click():
            type(self.application)
