import json
import time
import types
import asyncio
import collections
from uuid import uuid4
from multiprocessing import Process

from sanic import Sanic, response
from sanic.websocket import ConnectionClosed

from .utils import ReadWriteLock, index


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
        self._model = {}

    @rule('route', '/')
    async def display(self, request):
        return response.html(index())

    def run(self, *args, **kwargs):
        self.server.run(*args, **kwargs)

    def daemon(self, *args, **kwargs):
        Process(
            target=self.run,
            args=args,
            kwargs=kwargs,
            daemon=True,
        ).start()

    def _load_model(self, model):
        return update_differences(self._model, model, {})[1]

    def _load_event(self, event):
        return event

    def _sync(self, connection):
        updates = self._updates[-self._connections[connection]:]
        self._connections[connection] = 0
        return updates

    def _load(self, connection, update):
        added = 0
        for data in update:
            datatype = data['type']
            method = getattr(self, '_load_%s' % datatype)
            loaded = method(data[datatype])
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

    @rule('websocket', 'model/stream')
    async def _stream(self, request, socket):
        conn = uuid4().hex
        # initialize updates since last sync
        self._connections[conn] = 0
        try:
            empty = 0
            # send off the current state of the model as first message
            await socket.send(json.dumps(self._model))
            while True:
                async with self._lock.read():
                    send = self._sync(conn)
                await socket.send(json.dumps(send))
                recv = json.loads(await socket.recv())
                if recv:
                    async with self._lock.write():
                        self._load(conn, recv)
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
