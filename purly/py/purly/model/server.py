import json
import time
import types
import asyncio
from uuid import uuid4
from multiprocessing import Process

from sanic import Sanic, response
from sanic.websocket import ConnectionClosed
from sanic_cors import CORS

from .utils import diff


class rule:

    function = None

    def __init__(self, *args, **kwargs):
        self.name, *self.args = args
        self.kwargs = kwargs

    def __call__(self, function):
        self.function = function
        return self

    def __set_name__(self, cls, name):
        cls._rules.add(name)

    def __get__(self, obj, cls):
        if obj is None:
            return self
        else:
            return types.MethodType(self.setup, obj)

    def setup(self, obj, app):
        if self.function is not None:
            method = types.MethodType(self.function, obj)
            getattr(app, self.name)(*self.args, **self.kwargs)(method)
        else:
            return getattr(app, self.name)(*self.args, **self.kwargs)


class Server:

    _rules = set()

    def __init_subclass__(cls):
        cls._rules = cls._rules.copy()

    def __init__(self, refresh=25, cors=False):
        self._models = {}
        self._updates = {}
        self._connections = {}
        self._refresh_rate = 0 if refresh is None else (1 / refresh)
        self.server = Sanic()
        if cors:
            CORS(self.server)
        for name in self._rules:
            register = getattr(self, name)
            register(self.server)

    def run(self, *args, **kwargs):
        self.server.run(*args, **kwargs)

    def daemon(self, *args, **kwargs):
        return Process(
            target=self.run,
            args=args,
            kwargs=kwargs,
            daemon=True,
        ).start()

    @rule('websocket', '/model/<model>/stream')
    async def _stream(self, request, socket, model):
        conn = uuid4().hex
        self._connections.setdefault(model, []).append(conn)
        m = self._models.setdefault(model, {})
        # send off the current state of the model as first message
        initialize = {'header': {'type': 'update'}, 'content': m}
        self._updates[conn] = [initialize]
        # keep a reference to the model alive.
        try:
            while True:
                start = time.time()
                send = self._sync(conn)
                await socket.send(json.dumps(send))
                recv = json.loads(await socket.recv())
                if recv:
                    self._load(conn, model, recv)
                # throttle connections with few udpates
                stop = time.time()
                elapsed = stop - start
                if elapsed < self._refresh_rate:
                    await asyncio.sleep(self._refresh_rate - elapsed)
        except ConnectionClosed:
            pass
        except Exception:
            socket.close()
            raise
        finally:
            self._clean(model, conn)

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

    def _clean(self, model, conn):
        del self._updates[conn]
        self._connections[model].remove(conn)
        if not len(self._connections[model]):
            del self._connections[model]
            del self._models[model]
