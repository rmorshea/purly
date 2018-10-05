import os
from sanic import response

from .utils import STATIC_PATH
from .model import Server, rule

BOARD_PATH = os.path.join(STATIC_PATH, "board")


class Machine(Server):

    @rule('route', '/model/<model>/assets/<path:path>')
    async def _index(self, request, model, path):
        absolute = os.path.join(BOARD_PATH, *path.split('\n'))
        return await response.file(absolute)

    @rule('route', '/model/<model>/state')
    async def _state(self, request, model):
        return response.json(self._models[model])
