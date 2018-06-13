import json
import time
import types
import asyncio
import collections
from uuid import uuid4
from multiprocessing import Process

from sanic import Sanic, response
from sanic.websocket import ConnectionClosed

from .utils import ReadWriteLock, load_static_html, finalize


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
        self._updates = []
        self._models = {}

    def model(self, key):
        """Get a model.

        The model will be cleaned up when all references to it are lost.

        Parameters
        ----------
        key : hashable
            An identifier to associate with the model.

        Returns
        -------
        model : dict
            A model that is used as a "source of truth" for clients.
        """
        if key in self._models:
            m = self._models[key]
        else:
            m = self._models[key] = _Dict()
            @finalize(m)
            def clean():
                del self._models[key]
        return m

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
                <div data-purly-model="root"></div>
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

    def _load_model(self, conn, model, update):
        return update_differences(model, update, {})[1]

    def _load_event(self, conn, model, event):
        return event

    def _sync(self, connection):
        trim = len(self._updates) - self._connections[connection]
        updates = self._updates[trim:]
        self._connections[connection] = 0
        return updates

    def _load(self, connection, model, update):
        added = 0
        for data in update:
            datatype = data['type']
            method = getattr(self, '_load_%s' % datatype)
            loaded = method(connection, model, data[datatype])
            if loaded is not None:
                data[datatype] = loaded
                self._updates.append(data)
                added += 1
        for c in self._connections:
            self._connections[c] += added
        self._connections[connection] -= added

    def _clean(self):
        if self._updates:
            diff = len(self._updates) - max(self._connections.values())
            self._updates[:diff] = []

    @rule('websocket', '<model>/stream')
    async def _stream(self, request, socket, model):
        conn = uuid4().hex + model
        # initialize connection staleness.
        self._connections[conn] = 0
        # keep a reference to the model alive.
        model = self.model(model)
        try:
            empty = 0
            # send off the current state of the model as first message
            await socket.send(json.dumps(model))
            while True:
                async with self._lock.read():
                    send = self._sync(conn)
                await socket.send(json.dumps(send))
                recv = json.loads(await socket.recv())
                if recv:
                    async with self._lock.write():
                        self._load(conn, model, recv)
                if not send and not recv:
                    empty += 1
                    if empty > 2000:
                        await asyncio.sleep(1)
                else:
                    empty = 0
                self._clean()
        except ConnectionClosed:
            pass
        except Exception:
            socket.close()
            raise
        finally:
            del self._connections[conn]

    @rule('listener', 'after_server_start')
    async def _after_server_start(self, app, loop):
        # initialize anything that requires the current event loop
        self._lock = ReadWriteLock()


def update_differences(into, data, diff):
    for k in data:
        v = data[k]
        if isinstance(v, collections.Mapping):
            update_differences(
                into.setdefault(k, {}),
                v,
                diff.setdefault(k, {}),
            )
        elif k in into:
            if v is None:
                diff[k] = None
                del into[k]
            elif into[k] != v:
                diff[k] = into[k] = v
        elif v is not None:
            diff[k] = into[k] = v
    return into, diff
