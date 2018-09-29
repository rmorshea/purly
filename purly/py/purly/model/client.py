import json
import time
import websocket


class Client:

    def __init__(self, url):
        self._url = url
        self._updates = []
        self._socket = create_socket(url, connection_timeout=2)

    def sync(self):
        recv = []
        while True:
            data = self._socket.recv()
            if data:
                recv.extend(json.loads(data))
            outgoing = self._updates[:1000]
            self._socket.send(json.dumps(outgoing))
            self._updates[:1000] = []
            if not self._updates:
                break
        for incoming in recv:
            self._recv(incoming)

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
