import os
import sys
from asyncio import Event, Lock
from weakref import finalize as _finalize
if sys.version_info < (3, 7):
    from async_generator import asynccontextmanager
else:
    from contextlib import asynccontextmanager

HERE = os.path.dirname(__file__)
STATIC = os.path.join(HERE, 'static')
SCRIPTS = os.path.join(STATIC, 'scripts')


class ReadWriteLock:

    def __init__(self, loop=None, max_readers=5):
        self._readers = 0
        self._max_readers = max_readers
        self._lock = Lock(loop=loop)
        self._not_reading = Event(loop=loop)
        self._not_writing = Event(loop=loop)
        self._not_writing.set()

    @asynccontextmanager
    async def write(self):
        async with self._lock:
            self._not_writing.clear()
            await self._not_reading.wait()
            try:
                yield
            finally:
                self._not_writing.set()

    @asynccontextmanager
    async def read(self):
        while True:
            await self._not_writing.wait()
            if self._readers < self._max_readers:
                if not self._lock.locked():
                    break
        self._readers += 1
        if self._readers == 1:
            self._not_reading.clear()
        try:
            yield
        finally:
            self._readers -= 1
            if self._readers == 0:
                self._not_reading.set()


def load_static_html(*where, **format):
    if not where:
        where = SCRIPTS
    else:
        where = os.path.join(*where)

    html = ''
    for filename in sorted(os.listdir(where)):
        filename = os.path.join(where, filename)
        if os.path.isfile(filename) and os.path.splitext(filename)[1] == '.html':
            with open(filename) as f:
                result = f.read()
                for k, v in format.items():
                    result = result.replace('{{%s}}' % k, str(v))
                html += result
    return html


def finalize(obj, *args, **kwargs):
    """Turn ``weakref.finalize`` into a decorator."""
    def setup(function):
        _finalize(obj, function, *args, **kwargs)
        return function
    return setup
