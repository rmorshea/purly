import os
import sys
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

if sys.version_info < (3,6):
    error = "ERROR: %s requires Python version 3.6 or above." % name
    print(error, file=sys.stderr)
    sys.exit(1)

#-----------------------------------------------------------------------------
# requirements
#-----------------------------------------------------------------------------

requirements = [
    'sanic',
    'asyncio',
    'websocket-client',
    'websockets>=4.0,<5.0',
    'spectate>=0.2.1',
]

#-----------------------------------------------------------------------------
# Library Version
#-----------------------------------------------------------------------------

with open(os.path.join(root, '_version.py')) as f:
    _ = {}
    exec(f.read(), {}, _)
    version = _["__version__"]

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
        keywords=["interactive", "widgets", "DOM", "synchronization"],
        install_requires=requirements,
        classifiers=[
            'Intended Audience :: Developers',
            'Programming Language :: Python :: 3.6',
            ],
    )
