from IPython.display import HTML
from .utils import load_static_html


def output(uri):
    root = '<div data-purly-model="root"></div>'
    return HTML(root + load_static_html(uri=repr(uri)))
