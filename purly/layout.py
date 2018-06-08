import json
import time
import websocket
from uuid import uuid4
from spectate.mvc import view, Undefined, List
from weakref import WeakValueDictionary

from .html import HTML


def socket(uri, timeout=0, *args, **kwargs):
    start = time.time()
    while True:
        try:
            return websocket.create_connection(uri, timeout, *args, **kwargs)
        except ConnectionRefusedError:
            if time.time() - start > timeout:
                raise
            else:
                time.sleep(0.1)


class Layout:

    def __init__(self, uri):
        self._socket = socket(uri, timeout=2)
        self.children = List()

        @view(self.children)
        def capture_elements(change):
            self._capture_elements('root', self.children)

    def html(self, tag, *children, **attributes):
        return HTML(tag, *children, **attributes)

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

    def _update_children(self, element, children):
        return {
            'model': element,
            'update': 'children',
            'children': ''.join(map(str, children))
        }

    def _update_attributes(self, element, attributes):
        return {
            'model': element,
            'update': 'attributes',
            'attributes': attributes
        }

    def _update_style(self, element, style):
        style = '; '.join(
            '%s:%s' % (k.replace('_', '-'), v)
            for k, v in style.items()
        )
        return {
            'model': element,
            'update': 'attributes',
            'attributes': {'style': style}
        }

    def _capture_element(self, element):
        model = element.attributes['data-purly-model']

        @view(element.attributes)
        def capture_attributes(change):
            self._sync(self._update_attributes(model, element.attributes))

        @view(element.style)
        def capture_style(change):
            self._sync(self._update_style(model, element.style))

    def _capture_elements(self, parent, elements):
        self._sync(self._update_children(parent, elements))
        for e in elements:
            if isinstance(e, HTML):
                @view(e.children)
                def _capture(change):
                    model = e.attributes['data-purly-model']
                    self._capture_elements(model, e.children)
                self._capture_element(e)

    def _sync(self, send):
        recv = json.loads(self._socket.recv())
        # TODO: handle recieved update
        self._socket.send(json.dumps(send))
