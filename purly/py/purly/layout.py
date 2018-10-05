import os
from uuid import uuid4
from copy import deepcopy
from spectate import mvc
from weakref import WeakValueDictionary

from .model import Client
from .html import HTML
from .utils import finalize, STATIC_PATH

WIDGET_PATH = os.path.join(STATIC_PATH, "widget", "static", "js")

for filename in os.listdir(WIDGET_PATH):
    if filename.endswith(".js"):
        with open(os.path.join(WIDGET_PATH, filename), "r") as f:
            SCRIPT = f.read()
        break


class Layout(Client):

    _html_repr_shown = False

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
        """A decorator for functions t'ws://127.0.0.1:8000/model/color-wheel/stream'hat define HTML DOM structures.

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
        """Rich HTML display output."""
        uri = self._url.rsplit('/', 1)[0].split(':', 1)[1]
        socket_protocol = self._url.split(':', 1)[0]
        mount_id = "purly-mount-" + uuid4().hex
        endpoint = socket_protocol + ':' + uri + '/stream'
        built_script = ("" if Layout._html_repr_shown else f"<script>{SCRIPT}</script>")
        html = f"""
        <div id="{mount_id}"/>
        {built_script}
        <script>window.mountPurlyWidget("{endpoint}", "{mount_id}")</script>
        """
        Layout._html_repr_shown = True
        return html
