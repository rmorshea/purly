import os
from sanic import response

from .model import Server, rule

HERE = os.path.dirname(__file__)
REACT = os.path.join(HERE, 'react')


class Machine(Server):

    @rule('route', '/model/<model>/assets/<path:path>')
    async def _index(self, request, model, path):
        absolute = os.path.join(REACT, 'build', *path.split('\n'))
        return await response.file(absolute)

    @rule('route', '/model/<model>/state')
    async def _state(self, request, model):
        return response.json(self._models[model])
