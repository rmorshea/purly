import json
import inspect
from uuid import uuid4
from spectate import mvc


class HTML:

    def __init__(self, tag, *children, **attributes):
        attributes['key'] = uuid4().hex
        style = attributes.pop('style', {})

        self.tag = tag
        self.style = attributes['style'] = mvc.Dict(style)
        self.attributes = mvc.Dict(attributes)
        self.children = mvc.List(children)
        self.callbacks = {}

    def on(self, event, *update):
        def setup(function):
            uuid = uuid4().hex
            if not callable(function):
                raise TypeError('Expected a callable object.')
            keys = tuple(inspect.signature(function).parameters)
            self.attributes['on' + event] = {
                'callback': uuid,
                'keys': keys,
                'update': update,
            }
            self.callbacks[uuid] = function
            return function
        return setup

    def trigger(self, event):
        cb = event['callback']
        if cb in self.callbacks:
            self.callbacks[cb](**event['event'])

    def __eq__(self, other):
        return (
            self.tag == other.tag and
            self.attributes == other.attributes and
            self.children == other.children
        )

    def __repr__(self):
        attributes = ', '.join('%s=%r' % i for i in self.attributes.items())
        if attributes:
            attributes = ' ' + attributes
        style = '; '.join(
            '%s:%s' % (k.replace('_', '-'), v)
            for k, v in self.style.items()
        )
        if style:
            if attributes:
                attributes += ', '
            attributes += 'style=%r' % style
        children = '...' if self.children else ''
        return f'<{self.tag}{attributes}>{children}</{self.tag}>'

    def __str__(self):
        attributes = ', '.join('%s=%r' % i for i in self.attributes.items())
        if attributes:
            attributes = ' ' + attributes
        style = '; '.join(
            '%s:%s' % (k.replace('_', '-'), v)
            for k, v in self.style.items()
        )
        if style:
            if attributes:
                attributes += ', '
            attributes += 'style=%r' % style
        children = ''.join(map(str, self.children))
        return f'<{self.tag}{attributes}>{children}</{self.tag}>'
