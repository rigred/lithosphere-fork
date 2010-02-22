from halogen import Widget, Column, Label, Button, Area
from .util import Output, LabelSlider, quad, nested

class Node(object):
    def __init__(self, label, application):
        self.application = application
        application.add_node(self)
        self.column = Column()
        bar_area = Area().add_class('widget_bar')
        Label(label).append_to(bar_area)
        Button().append_to(bar_area).on_click = self.delete
        self.texture = application.create_texture()
        self.widget = Widget(bar_area, self.column).add_class('node').append_to(application.workspace)

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
        self.application.remove_node(self)

    def reconnect(self, data, instances):
        pass
