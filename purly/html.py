import json
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
        self.events = mvc.Dict()

    def on(self, event, *data):
        def setup(function):
            self.events[event] = (function, data)
            return function
        return setup

    def trigger(self, event):
        etype = event['type']
        if etype in self.events:
            function, _ = self.events[etype]
            function(event[etype])

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
