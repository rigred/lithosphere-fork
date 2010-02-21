from halogen import Widget, Column
from .util import Output, LabelSlider, quad, nested

class Node(object):
    def __init__(self, label, application):
        self.application = application
        application.add_node(self)
        self.column = Column()
        self.texture = application.create_texture()
        self.widget = Widget(label, self.column).add_class('node').append_to(application.workspace)

    def get_parameters(self):
        return []
    def set_parameters(self, values):
        pass
    parameters = property(get_parameters, set_parameters)
    del get_parameters, set_parameters

    @property
    def sources(self):
        return dict()

    def delete(self):
        self.output.delete()
        self.texture.delete()
        for name, slot in self.sources.items():
            if slot.source:
                slot.content.delete()
        self.widget.remove()

    def reconnect(self, data, instances):
        pass
