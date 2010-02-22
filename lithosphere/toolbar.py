# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from halogen import Column, Row, Button, Node

class Toolbar(object):
    def __init__(self, application):
        self.application = application
        self.row = Row(id='toolbar').append_to(application.work_area)
        self.col1 = Column().append_to(self.row)
        self.col2 = Column().append_to(self.row)
        
        Button('Open').append_to(self.col1).on_click = application.dialogs.open
        Button('Save').append_to(self.col1).on_click = application.dialogs.save
        Button('New').append_to(self.col1).on_click = application.empty
        Node().add_class('seperator').append_to(self.col1)


    def add(self, type):
        if self.col1.length < 8:
            button = Button(type.__name__).append_to(self.col1)
        else:
            button = Button(type.__name__).append_to(self.col2)

        @button.event
        def on_click():
            type(self.application)
