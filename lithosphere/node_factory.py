# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

import noise, binops, filters, mix, adjust, color_source

modules = noise, binops, filters, mix, adjust, color_source

class NodeFactory(object):
    def __init__(self, application):
        self.application = application
        self.types = dict(
            (node_type.__name__, node_type)
            for node_type in self.nodes
        )

        toolbar = application.toolbar
        for type in noise.nodes + color_source.nodes:
            toolbar.sources.add(type)

        for type in binops.nodes + mix.nodes:
            toolbar.operators.add(type)

        for type in filters.nodes + adjust.nodes:
            toolbar.filters.add(type)
       
    @property
    def nodes(self):
        for module in modules:
            for node_type in module.nodes:
                yield node_type

    def create(self, data):
        node_type = self.types[data['type']]
        instance = node_type(self.application)
        instance.parameters = data['parameters']
        offset = data['offset']
        instance.widget.rect.x, instance.widget.rect.y = offset['x'], offset['y']
        instance.widget.layout()
        return instance
