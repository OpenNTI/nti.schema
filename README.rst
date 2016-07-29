============
 nti.schema
============

.. image:: https://travis-ci.org/NextThought/nti.schema.svg?branch=master
  :target: https://travis-ci.org/NextThought/nti.schema

.. image:: https://coveralls.io/repos/github/NextThought/nti.schema/badge.svg
  :target: https://coveralls.io/github/NextThought/nti.schema

nti.schema offers a set of classes and functions that make
schema-based development with zope.schema easier.

For complete details and the changelog, see the `documentation <http://ntischema.readthedocs.io/>`_.

Overview
--------

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
