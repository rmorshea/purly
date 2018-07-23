from sanic import response

from .model import Server, rule
from .utils import load_static_html


class Machine(Server):

    @rule('route', '/<model>/index')
    async def _index(self, request, model):
        html = '''
        <!DOCTYPE html>
        <html>
            <head>
                <meta charset="UTF-8">
                <title>%s</title>
            </head>
            <body>
                %s
            </body>
        </html>
        '''
        if 'https' in (request.scheme, request.headers.get('x-scheme')):
            protocol = 'wss'
        else:
            protocol = 'ws'
        return response.html(html % (model, load_static_html(uri=(
            f"'{protocol}://' + document.location.hostname + ':' "
            "+ window.location.port + document.location.pathname"
        ))))

    @rule('route', '/<model>/state')
    async def _state(self, request, model):
        return response.json(self._models[model])
