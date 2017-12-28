from codecs import open
from os.path import abspath, dirname, join
from setuptools import Command, find_packages, setup

dir = abspath(dirname(__file__))
with open(join(dir, 'README.txt'), encoding='utf-8') as file:
    fulldescription = file.read()

setup(
    name = 'openmoves',
    version = '1',
    description = 'Library for analysing OPT data',
    long_description = fulldescription,
    author = 'Sam Amin',
    author_email = 'samamin@ucla.edu',
    packages = find_packages(exclude=['docs', 'tests*']),
    #install_requires = ['docopt', 'socket', 'time', 'json', 'time', 'random', 
	#'sklearn', 'shapely', 'descartes', 'matplotlib', 'numpy'],
    entry_points = {
        'console_scripts': [
            'openmoves=openmoves.cli:main',
        ],
    },
)
