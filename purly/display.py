from IPython.display import HTML
from .utils import load_static_html


def output(uri):
    return HTML(load_static_html(uri=repr(uri)))
