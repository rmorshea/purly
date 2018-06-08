import os
import sys
from asyncio import Event, Lock
if sys.version_info < (3, 7):
    from async_generator import asynccontextmanager
else:
    from contextlib import asynccontextmanager

HERE = os.path.join(os.path.dirname(__file__), 'static')


class ReadWriteLock:

    def __init__(self, loop=None):
        self._readers = 0
        self._lock = Lock(loop=loop)
        self._not_reading = Event(loop=loop)
        self._not_writing = Event(loop=loop)
        self._not_writing.set()

    @asynccontextmanager
    async def write(self):
        async with self._lock:
            self._not_writing.clear()
            await self._not_reading.wait()
            yield
        self._not_writing.set()

    @asynccontextmanager
    async def read(self):
        while True:
            await self._not_writing.wait()
            if not self._lock.locked():
                break
        self._readers += 1
        if self._readers == 1:
            self._not_reading.clear()
        yield
        self._readers -= 1
        if self._readers == 0:
            self._not_reading.set()


def inject(where=HERE):
    for filename in os.listdir(os.path.join(where, 'inject')):
        filename = os.path.join(where, 'inject', filename)
        if os.path.isfile(filename) and os.path.splitext(filename)[1] == '.html':
            yield filename


def index(where=HERE):
    injection = ''
    for filename in inject(where):
        with open(filename) as i:
            injection += i.read()
    with open(os.path.join(where, 'index.html')) as index:
        template = index.read()
        fill = dict(title='Purly', inject=injection)
        return template.format(**fill)
