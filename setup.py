#!/usr/bin/env python
from setuptools import setup, find_packages
import codecs

version = '1.0.2a1'

entry_points = {
}

def _read(fname):
    with codecs.open(fname, encoding='utf-8') as f:
        return f.read()

setup(
    name = 'nti.schema',
    version = version,
    author = 'Jason Madden',
    author_email = 'open-source@nextthought.com',
    description = ('Zope schema related support'),
    long_description = _read('README.rst') + '\n\n' + _read('CHANGES.rst'),
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
    include_package_data=True,
    install_requires=[
        'setuptools',
        'zope.schema',
        'zope.i18nmessageid',
        'zope.browserresource',
        'zope.vocabularyregistry',
        'dm.zope.schema', # PY3: Not  ported yet
        'dolmen.builtins',
        'plone.i18n < 3.0', # PY3: Not ported yet; version 3 adds hard dep on Products.CMFCore/Zope2
    ],
    extras_require={
        'test':[
            'nose2',
            'pyhamcrest',
            'nti.testing',
            'zope.dottedname',
            'transaction'
        ]
    },
    namespace_packages=['nti'],
    entry_points=entry_points,
    test_suite='nose2.compat.unittest.collector'
)
