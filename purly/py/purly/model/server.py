import json
import time
import types
import asyncio
from uuid import uuid4
from multiprocessing import Process

from sanic import Sanic, response
from sanic.websocket import ConnectionClosed
from sanic_cors import CORS

from .utils import diff, diritems


class rule:

    function = None

    def __new__(cls, *args, **kwargs):
        def __init__(function):
            self = super(rule, cls).__new__(cls)
            self.__init__(function, *args, **kwargs)
            return self
        return __init__

    def __init__(self, *args, **kwargs):
        self.function = args[0]
        self.name, *self.args = args[1:]
        self.kwargs = kwargs

    def __get__(self, obj, cls):
        if obj is not None:
            return types.MethodType(self.function, obj)
        else:
            return self

    def setup(self, obj, app):
        if self.function is not None:
            method = types.MethodType(self.function, obj)
            getattr(app, self.name)(*self.args, **self.kwargs)(method)
        else:
            return getattr(app, self.name)(*self.args, **self.kwargs)


class Server:

    def __init__(self, refresh=25, cors=False):
        self._refresh_rate = 0 if refresh is None else (1 / refresh)
        self._server = Sanic()
        if cors:
            CORS(self._server)
        for k, v in diritems(type(self)):
            if isinstance(v, rule):
                v.setup(self, self._server)
        self._init_server(self._server)

    def run(self, *args, **kwargs):
        self._server.run(*args, **kwargs)

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
        self._init_connection(conn, model)
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
            self._clean(conn, model)

    def _init_server(self, server):
        self._models = {}
        self._updates = {}
        self._connections = {}

    def _init_connection(self, conn, model):
        self._connections.setdefault(model, set()).add(conn)
        state = self._models.setdefault(model, {})
        # send off the current state of the model as first message
        initialize = {'header': {'type': 'update'}, 'content': state}
        self._updates[conn] = [initialize]

    def _load_update(self, model, update):
        return diff(self._models[model], update)

    def _load_signal(self, model, signal):
        return signal

    def _sync(self, conn):
        send = self._updates[conn][:]
        self._updates[conn].clear()
        return send

    def _load(self, conn, model, update):
        messages = []
        for data in update:
            datatype = data['header']['type']
            method = getattr(self, '_load_%s' % datatype)
            loaded = method(model, data['content'])
            if loaded:
                data[datatype] = loaded
                messages.append(data)
        self._to_sync(conn, model, messages)

    def _to_sync(self, conn, model, messages):
        for c in self._connections[model].difference({model}):
            self._updates[c].extend(messages)

    def _clean(self, conn, model):
        del self._updates[conn]
        self._connections[model].remove(conn)
        if not len(self._connections[model]):
            del self._connections[model]
            del self._models[model]
