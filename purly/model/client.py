import json
import time
import websocket


class Client:

    def __init__(self, uri):
        self._uri = uri
        self._updates = []
        self._socket = create_socket(uri, connection_timeout=2)

    def sync(self):
        recv = json.loads(self._socket.recv())
        for msg in recv:
            self._recv(msg)
        self._socket.send(json.dumps(self._updates))
        self._updates.clear()

    def serve(self, function=None):
        while True:
            if function is not None:
                try:
                    function()
                except StopIteration:
                    break
            self.sync()

    def _send(self, content, header):
        self._updates.append({
            'header': header,
            'content': content,
        })

    def _recv(self, msg):
        datatype = msg['header']['type']
        method = '_on_%s' % datatype
        if hasattr(self, method):
            getattr(self, method)(msg['content'])


def create_socket(uri, *args, **kwargs):
    start = time.time()
    while True:
        try:
            return websocket.create_connection(uri, *args, **kwargs)
        except ConnectionRefusedError:
            if time.time() - start > kwargs.get('connection_timeout', 0):
                raise
