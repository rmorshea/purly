from IPython.display import display, HTML
from .utils import index, injection


def output(uri):
    scripts = ''.join(injection())
    substitute = "'ws://' + document.domain + ':' + location.port + '/model/stream'"
    return HTML(index(inject=scripts.replace(substitute, '%r' % uri)))
