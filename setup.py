from codecs import open
from os.path import abspath, dirname, join
from setuptools import Command, find_packages, setup
from subprocess import call
from compileall import compile_dir
from openmoves import __version__

dir = abspath(dirname(__file__))
with open(join(dir, 'README.txt'), encoding='utf-8') as file:
    fulldescription = file.read()

compile_dir(join(dir, '/openmoves/commands/library'))

setup(
    name = 'openmoves',
    version = __version__,
    description = 'Library for analysing OPT data',
    long_description = fulldescription,
    author = 'Sam Amin',
    author_email = 'samamin@ucla.edu',
    keywords = 'cli',
    packages = find_packages(exclude=['docs']),
    install_requires = ['docopt', 'shapely', 'descartes', 'matplotlib', 'numpy', 'sklearn', 'scipy', 'cython', 'fastdtw'],
    entry_points = {
        'console_scripts': [
            'openmoves=openmoves.cli:main',
        ],
    },
)
