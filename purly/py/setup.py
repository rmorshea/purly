from __future__ import print_function

import os
import sys
import shutil
from glob import glob
from setuptools import find_packages
from distutils.core import setup

# the name of the project
name = "purly"

# basic paths used to gather files
here = os.path.abspath(os.path.dirname(__file__))
root = os.path.join(here, name)

#-----------------------------------------------------------------------------
# Python Version Check
#-----------------------------------------------------------------------------

if sys.version_info < (3,6) or sys.version_info >= (3, 7):
    error = "ERROR: %s requires Python version 3.6." % name
    print(error, file=sys.stderr)
    sys.exit(1)

#-----------------------------------------------------------------------------
# requirements
#-----------------------------------------------------------------------------

requirements = [
    'sanic',
    'asyncio',
    'websocket-client',
    'websockets',
    'spectate>=0.2.1',
]

#-----------------------------------------------------------------------------
# Library Version
#-----------------------------------------------------------------------------

with open(os.path.join(root, '__init__.py')) as f:
    for line in f.read().split("\n"):
        if line.startswith("__version__ = "):
            version = eval(line.split("=", 1)[1])
            break
    else:
        print("No version found in purly/__init__.py")
        sys.exit(1)

#-----------------------------------------------------------------------------
# Library Description
#-----------------------------------------------------------------------------

with open(os.path.join(here, 'README.md')) as f:
    long_description = f.read()

#-----------------------------------------------------------------------------
# Install It
#-----------------------------------------------------------------------------

if __name__ == '__main__':
    setup(
        name=name,
        version=version,
        packages=find_packages(),
        include_package_data=True,
        description="Control the web with Python",
        long_description=long_description,
        long_description_content_type='text/markdown',
        author="Ryan Morshead",
        author_email="ryan.morshead@gmail.com",
        url="https://github.com/rmorshea/purly",
        license='MIT',
        platforms="Linux, Mac OS X, Windows",
        keywords=["interactive", "widgets", "DOM", "synchronization", "React"],
        install_requires=requirements,
        classifiers=[
            'Intended Audience :: Developers',
            'Programming Language :: Python :: 3.6',
            ],
    )
