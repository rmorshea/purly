import os
from sanic import response

from .model import Server, rule

HERE = os.path.dirname(__file__)
REACT = os.path.join(HERE, 'react')


class Machine(Server):

    _static = rule('static', '/hub/static', os.path.join(REACT, 'build', 'static'))
    _public = rule('static', '/public', os.path.join(REACT, 'public'))

    @rule('route', '/model/<model>/index')
    async def _index(self, request, model):
        with open(os.path.join(REACT, 'build', 'index.html')) as f:
            return response.html(f.read())

    @rule('route', '/model/<model>/state')
    async def _state(self, request, model):
        return response.json(self._models[model])
