import json
import time
import types
import asyncio
from uuid import uuid4
from multiprocessing import Process

from sanic import Sanic, response
from sanic.websocket import ConnectionClosed

from .utils import ReadWriteLock, load_static_html, finalize, diff


class _Dict(dict):
    """can't create weakref to ``dict``"""


class rule:

    def __new__(cls, *args, **kwargs):
        new = super().__new__
        def __init__(function):
            self = new(cls)
            self.__init__(function, *args, **kwargs)
            return self
        return __init__

    def __init__(self, function, *args, **kwargs):
        self.function = function
        self.name, *self.args = args
        self.kwargs = kwargs

    def __set_name__(self, cls, name):
        cls._rules.add(name)

    def __get__(self, obj, cls):
        if obj is None:
            return self
        else:
            return types.MethodType(self.__call__, obj)

    def __call__(self, obj, app):
        method = types.MethodType(self.function, obj)
        getattr(app, self.name)(*self.args, **self.kwargs)(method)


class Machine:

    _rules = set()

    def __init_subclass__(cls):
        self._rules = self._rules.copy()

    def __init__(self):
        self.server = Sanic()
        for name in self._rules:
            register = getattr(self, name)
            register(self.server)
        self._connections = {}
        self._updates = {}
        self._models = {}

    @rule('route', '/<model>/index')
    async def display(self, request, model):
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
        uri = f"'ws://' + document.domain + ':' + location.port + '/{model}/stream'"
        return response.html(html % (model, load_static_html(uri=uri)))

    def run(self, *args, **kwargs):
        self.server.run(*args, **kwargs)

    def daemon(self, *args, **kwargs):
        Process(
            target=self.run,
            args=args,
            kwargs=kwargs,
            daemon=True,
        ).start()

    def _load_update(self, model, update):
        return diff(self._models[model], update)

    def _load_signal(self, model, signal):
        return signal

    def _sync(self, conn):
        index = len(self._updates[conn])
        send = self._updates[conn][:index]
        self._updates[conn][:index] = []
        return send

    def _load(self, conn, model, update):
        distribute = []
        for data in update:
            datatype = data['header']['type']
            method = getattr(self, '_load_%s' % datatype)
            loaded = method(model, data['content'])
            if loaded:
                data[datatype] = loaded
                distribute.append(data)
        for c in self._connections[model]:
            if c != conn:
                self._updates[c].extend(distribute)

    @rule('websocket', '<model>/stream')
    async def _stream(self, request, socket, model):
        conn = uuid4().hex
        self._connections.setdefault(model, []).append(conn)
        m = self._models.setdefault(model, {})
        # send off the current state of the model as first message
        initialize = {'header': {'type': 'update'}, 'content': m}
        self._updates[conn] = [initialize]
        # keep a reference to the model alive.
        try:
            empty = 0
            while True:
                send = self._sync(conn)
                await socket.send(json.dumps(send))
                recv = json.loads(await socket.recv())
                if recv:
                    self._load(conn, model, recv)
                # throttle connections with few udpates
                if not send and not recv:
                    if empty > 2000:
                        await asyncio.sleep(0.5)
                    else:
                        empty += 1
                else:
                    empty = 0
        except ConnectionClosed:
            pass
        except Exception:
            socket.close()
            raise
        finally:
            self._clean(model, conn)

    def _clean(self, model, conn):
        del self._updates[conn]
        self._connections[model].remove(conn)
        if not len(self._connections[model]):
            del self._connections[model]
            del self._models[model]
