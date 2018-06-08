import json
from uuid import uuid4
from spectate import mvc


class HTML:

    def __init__(self, tag, *children, **attributes):
        self.tag = tag
        self.style = mvc.Dict(attributes.pop('style', {}))
        attributes['data-purly-model'] = uuid4().hex
        self.attributes = mvc.Dict(attributes)
        self.children = mvc.List(children)

    def __eq__(self, other):
        return (
            self.tag == other.tag and
            self.style == other.style and
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
