from copy import deepcopy
from spectate import mvc
from weakref import WeakValueDictionary

from .model import Client
from .html import HTML
from .utils import finalize


class Layout(Client):

    def __init__(self, url):
        super().__init__(url)
        self.children = mvc.List()
        self._contains = WeakValueDictionary()

        @mvc.view(self.children)
        def capture_elements(change):
            self._update_children('root', self.children)

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

    def _update_children(self, parent_key, children):
        serialized = []
        for c in children:
            if isinstance(c, HTML):
                c.attributes["parent_key"] = parent_key
                serialized.append({
                    'type': 'ref',
                    'ref': c.attributes['key'],
                })
            else:
                serialized.append(str(c))
        self._send({parent_key: {'children': serialized}}, {'type': 'update'})

    def _update_initialize(self, element):
        key = element.attributes['key']
        self._send({key: {'tagName': element.tag}}, {'type': 'update'})

    def _update_attributes(self, key, attributes):
        self._send({key: {'attributes': deepcopy(attributes)}}, {'type': 'update'})

    def _update_propogate(self, key):
        message = {}
        while key not in (None, 'root'):
            if key not in self._contains:
                break
            element = self._contains[key]
            message[key] = {'signature': hex(hash(element))}
            key = element.attributes["parent_key"]
        self._send(message, {'type': 'update'})

    def _capture_element(self, element):
        key = element.attributes['key']

        if key not in self._contains:

            @mvc.view(element.attributes)
            def capture_attributes(changes):
                attributes = {}
                for c in changes:
                    new = c['new']
                    if new is mvc.Undefined:
                        new = None
                    attributes[c['key']] = new
                self._update_attributes(key, attributes)
                self._update_propogate(key)

            @mvc.view(element.style)
            def capture_style(changes):
                style = {}
                for c in changes:
                    new = c.new
                    if new is mvc.Undefined:
                        new = None
                    style[c.key] = new
                self._update_attributes(key, {'style': style})
                self._update_propogate(key)

            @mvc.view(element.children)
            def capture_children(changes):
                self._update_children(key, element.children)
                self._update_propogate(key)

            @finalize(element)
            def _sync_delete():
                self._send({key: None}, {'type': 'update'})
                self._update_propogate(key)

            self._contains[key] = element
            self._update_initialize(element)
            self._update_attributes(key, element.attributes)
            self._update_children(key, element.children)

    def _on_update(self, msg):
        for key, update in msg.items():
            if key in self._contains:
                element = self._contains[key]
                if 'attributes' in update:
                    element.attributes.update(update['attributes'])

    def _on_signal(self, msg):
        for key, event in msg.items():
            if key in self._contains:
                self._contains[key].trigger(event)

    def _repr_html_(self):
        """Rich display output for ipython."""
        uri = self._url.rsplit('/', 1)[0].split(':', 1)[1]
        socket_protocol = self._url.split(':', 1)[0]
        if socket_protocol == "wss":
            http_protocol = "https"
        else:
            http_protocol = "http"
        url = http_protocol + ':' + uri + '/assets/index.html'
        form = '<iframe src=%r frameBorder="0"></iframe>'
        return form % url
