import os
from setuptools import setup, find_packages

VERSION = '0.1.0'

setup(
	namespace_packages = ['tiddlywebplugins'],
	name = 'tiddlywebplugins.mongodb',
	version = VERSION,
	description = 'A ',
	long_description=file(os.path.join(os.path.dirname(__file__), 'README')).read(),
	author = 'Ben Paddock',
	url = 'http://pypi.python.org/pypi/tiddlywebplugins.mongodb',
	packages = find_packages(exclude=['test']),
	author_email = 'pads@thisispads.me.uk',
	platforms = 'Posix; MacOS X; Windows',
	install_requires = ['tiddlyweb', 'pymongo'],
	extras_require = {
		'testing': ['pytest', 'mock', 'tiddlywebplugins.utils'],
		'coverage': ['pytest-cov', 'python-coveralls'],
		'style': ['pep8']
	},
	zip_safe = False,
	)
