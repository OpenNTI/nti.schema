============
 nti.schema
============

.. image:: https://img.shields.io/pypi/v/nti.schema.svg
        :target: https://pypi.python.org/pypi/nti.schema/
        :alt: Latest release

.. image:: https://img.shields.io/pypi/pyversions/nti.schema.svg
        :target: https://pypi.org/project/nti.schema/
        :alt: Supported Python versions

.. image:: https://travis-ci.org/NextThought/nti.schema.svg?branch=master
        :target: https://travis-ci.org/NextThought/nti.schema

.. image:: https://coveralls.io/repos/github/NextThought/nti.schema/badge.svg
        :target: https://coveralls.io/github/NextThought/nti.schema

.. image:: http://readthedocs.org/projects/ntischema/badge/?version=latest
        :target: http://ntischema.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

nti.schema includes utilities for working with schema-driven
development using `zope.schema <http://docs.zope.org/zope.schema/>`_.

For complete details and the changelog, see the `documentation <http://ntischema.readthedocs.io/>`_.

Overview
========

Some of the most useful features include:

- ``nti.schema.interfaces.find_most_derived_interface`` for finding a
  bounded interface.
- ``nti.schema.eqhash.EqHash`` is a class-decorator for creating
  efficient, correct implementations of equality and hashing.
- ``nti.schema.field`` contains various schema fields, including a
  ``Variant`` type and more flexible collection types, all of which
  produce better validation errors.
- ``nti.schema.fieldproperty`` contains field properties that can
  adapt to interfaces or decode incoming text. The function
  ``createDirectFieldProperties`` can assign just the necessary
  properties automatically.
