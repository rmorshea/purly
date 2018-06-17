import os
from weakref import finalize as _finalize

HERE = os.path.dirname(__file__)
STATIC = os.path.join(HERE, 'static')
SCRIPTS = os.path.join(STATIC, 'scripts')


def load_static_html(*where, **format):
    if not where:
        where = SCRIPTS
    else:
        where = os.path.join(*where)

    html = ''
    for filename in sorted(os.listdir(where)):
        filename = os.path.join(where, filename)
        if os.path.isfile(filename) and os.path.splitext(filename)[1] == '.html':
            with open(filename) as f:
                result = f.read()
                for k, v in format.items():
                    result = result.replace('{{%s}}' % k, str(v))
                html += result
    return html


def finalize(obj, *args, **kwargs):
    """Turn ``weakref.finalize`` into a decorator."""
    def setup(function):
        _finalize(obj, function, *args, **kwargs)
        return function
    return setup
