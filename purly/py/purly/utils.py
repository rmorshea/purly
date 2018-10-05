import os
from weakref import finalize as _finalize

HERE = os.path.dirname(__file__)
STATIC_PATH = os.path.join(HERE, "static")


def finalize(obj, *args, **kwargs):
    """Turn ``weakref.finalize`` into a decorator."""
    def setup(function):
        _finalize(obj, function, *args, **kwargs)
        return function
    return setup
