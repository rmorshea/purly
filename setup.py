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
    'spectate>=0.2.1',
]

if sys.version_info < (3, 7):
    requirements.append('async_generator')

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
# Static Files
#-----------------------------------------------------------------------------

def package_files(*path_to_files):
    directory = os.path.join(*path_to_files)
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


static_files = package_files(root, 'static')

#-----------------------------------------------------------------------------
# Install It
#-----------------------------------------------------------------------------

if __name__ == '__main__':
    setup(
        name=name,
        version=version,
        packages=find_packages(),
        package_data={'': static_files},
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
