#!/usr/bin/env python
from setuptools import setup, find_packages
import codecs

VERSION = '1.0.2a1'

entry_points = {
}

setup(
	name = 'nti.schema',
	version = VERSION,
	author = 'Jason Madden',
	author_email = 'open-source@nextthought.com',
	description = ('Zope schema related support'),
	long_description = codecs.open('README.rst', encoding='utf-8').read() + '\n\n' + codecs.open('CHANGES.rst', encoding='utf-8').read(),
	license = 'Apache',
	keywords = 'zope schema',
	url = 'https://github.com/NextThought/nti.schema',
	classifiers = [
		'Development Status :: 5 - Production/Stable',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: Apache Software License',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.7',
		'Framework :: Zope3'
		],
	packages=find_packages('src'),
	package_dir={'': 'src'},
	install_requires=[
		'setuptools',
		'zope.schema',
		'zope.i18nmessageid',
		'zope.browserresource',
		'zope.vocabularyregistry',
		'dm.zope.schema', # PY3: Not  ported yet
		'dolmen.builtins',
		'plone.i18n', # PY3: Not ported yet
	],
	extras_require={
		'test':[
			'nose2',
			'pyhamcrest',
			'zope.testing',
			'zope.dottedname',
			'transaction'
		]
	},
	namespace_packages=['nti'],
	entry_points=entry_points,
	test_suite='nose2.compat.unittest.collector'
)
