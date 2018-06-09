import json
import time
import websocket
from uuid import uuid4
from spectate import mvc
from weakref import finalize

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
        # TODO: handle updates
        self._socket.recv()
        self.children = mvc.List()

        @mvc.view(self.children)
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
        self._sync({model: {'children': serialized}})

    def _update_initialize(self, element):
        model_id = element.attributes['data-purly-model']
        init = {'attributes': {}, 'children': [], 'tag': element.tag}
        self._sync({model_id: init})
        self._update_attributes(model_id, element.attributes)

    def _update_attributes(self, model, attributes):
        self._sync({model: {'attributes': attributes}})

    def _capture_element(self, element):
        model = element.attributes['data-purly-model']
        @mvc.view(element.attributes)
        def capture_attributes(change):
            self._update_attributes(model, element.attributes)
        @mvc.view(element.children)
        def capture_children(change):
            self._capture_elements(model, element.children)
        self._update_initialize(element)
        def _sync_delete():
            self._sync({model_id: None})
        finalize(element, _sync_delete)

    def _capture_elements(self, parent, elements):
        for e in elements:
            if isinstance(e, HTML):
                self._capture_element(e)
        self._update_children(parent, elements)

    def _sync(self, send):
        recv = json.loads(self._socket.recv())
        # TODO: handle recieved update
        self._socket.send(json.dumps(send))
