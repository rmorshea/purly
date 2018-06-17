from spectate import mvc
from weakref import WeakValueDictionary

from .model import Client
from .html import HTML
from .display import output
from .utils import finalize


class Layout(Client):

    def __init__(self, uri):
        super().__init__(uri)
        self.children = mvc.List()
        self._contains = WeakValueDictionary()

        @mvc.view(self.children)
        def capture_elements(change):
            self._capture_elements('root', self.children)

    def html(self, tag, *children, **attributes):
        new = HTML(tag, *children, **attributes)
        self._capture_element(new)
        return new

    def __call__(self, constructor):
        """A decorator for functions that define HTML DOM structures.

        The function should accept on argument - an :class:`HTML` object. It can
        return one or more :class:`HTML` objects, or other layout functions in order
        to specify what its children elements should be.
        """
        if isinstance(constructor, HTML):
            self._register(constructor)
            return constructor
        elif not callable(constructor):
            return constructor

        tag = constructor.__annotations__.get('return', tag)
        if tag is None:
            raise ValueError('%r has not defined tag' % constructor)
        self = HTML(tag)

        children = constructor(self)
        if children is not None:
            with self.hold():
                if isinstance(children, HTML):
                    self._register(children)
                    self.children.append(children)
                elif callable(children):
                    self.children.append(self.layout(children))
                else:
                    self.children.extend(map(self.layout, children))
        return self

    def _update_children(self, model, children):
        serialized = []
        for c in children:
            if isinstance(c, HTML):
                serialized.append({
                    'type': 'ref',
                    'ref': c.attributes['data-purly-model'],
                })
            else:
                serialized.append({
                    'type': 'str',
                    'str': str(c)
                })
        self._send({model: {'children': serialized}}, {'type': 'update'})

    def _update_initialize(self, element):
        model = element.attributes['data-purly-model']
        self._send({model: {'tag': element.tag}}, {'type': 'update'})

    def _update_attributes(self, model, attributes):
        self._send({model: {'attributes': attributes}}, {'type': 'update'})

    def _update_events(self, model, events):
        update = {}
        for etype, (_, data) in events.items():
            update[etype] = data
        self._send({model: {'events': update}}, {'type': 'update'})

    def _capture_element(self, element):
        model = element.attributes['data-purly-model']

        if model not in self._contains:

            @mvc.view(element.attributes)
            def capture_attributes(change):
                attributes = {}
                for c in change:
                    new = c['new']
                    if new is mvc.Undefined:
                        new = None
                    attributes[c['key']] = new
                self._update_attributes(model, attributes)

            @mvc.view(element.children)
            def capture_children(change):
                self._capture_elements(model, element.children)

            @mvc.view(element.events)
            def capture_events(change):
                self._update_events(model, element.events)

            @finalize(element)
            def _sync_delete():
                self._send({model: None}, {'type': 'update'})

            self._contains[model] = element
            self._update_initialize(element)
            self._update_events(model, element.events)
            self._update_attributes(model, element.attributes.copy())
            self._capture_elements(model, element.children)

    def _capture_elements(self, parent, elements):
        self._update_children(parent, elements)

    def _on_signal(self, msg):
        for model, event in msg.items():
            if model in self._contains:
                self._contains[model].trigger(event)

    def _repr_html_(self):
        """Rich display output for ipython."""
        return output(self._uri).data
