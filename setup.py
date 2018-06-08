from __future__ import print_function
from setuptools import find_packages

# the name of the project
name = "purly"

#-----------------------------------------------------------------------------
# Minimal Python version sanity check
#-----------------------------------------------------------------------------

import sys

if sys.version_info < (3,6):
    error = "ERROR: %s requires Python version 3.6 or above." % name
    print(error, file=sys.stderr)
    sys.exit(1)

#-----------------------------------------------------------------------------
# get on with it
#-----------------------------------------------------------------------------

import os
from glob import glob

from distutils.core import setup

here = os.path.abspath(os.path.dirname(__file__))
root = os.path.join(here, name)


requirements = [
    'sanic',
    'asyncio',
    'websocket-client',
    'spectate>=0.2.1',
]

if sys.version_info < (3, 7):
    requirements.append('async_generator')


with open(os.path.join(root, '_version.py')) as f:
    namespace = {}
    exec(f.read(), {}, namespace)
    version = namespace["__version__"]


with open(os.path.join(here, 'README.md')) as f:
    long_description = f.read()


if __name__ == '__main__':
    setup(
        name=name,
        version=version,
        packages=find_packages(),
        description="Control the web with Python",
        long_description=long_description,
        long_description_content_type='text/markdown',
        author="Ryan Morshead",
        author_email="ryan.morshead@gmail.com",
        url="https://github.com/rmorshea/purly",
        license='MIT',
        platforms="Linux, Mac OS X, Windows",
        keywords=["interactive", "widgets", "DOM", "synchronization"],
        install_requires=requirements,
        classifiers=[
            'Intended Audience :: Developers',
            'Programming Language :: Python :: 3.6',
            ],
    )
