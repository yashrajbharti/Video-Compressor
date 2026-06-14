import os
import sys
from setuptools import setup

APP = ['app.py']
DATA_FILES = ['icon-256.png']

# Locate libraries (common dependency issues in Conda/Miniforge environments)
libs_to_bundle = [
    os.path.join(sys.prefix, 'lib', 'libffi.8.dylib'),
    os.path.join(sys.prefix, 'lib', 'libtcl8.6.dylib'),
    os.path.join(sys.prefix, 'lib', 'libtk8.6.dylib')
]
frameworks = [lib for lib in libs_to_bundle if os.path.exists(lib)]

OPTIONS = {
    'iconfile': 'icon.icns',
    'argv_emulation': False,
    'frameworks': frameworks,
    'packages': ['tkinterdnd2']
}

setup(
    name="Video Compressor",
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
