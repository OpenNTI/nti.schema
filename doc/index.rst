============
 nti.schema
============

nti.schema includes utilities for working with schema-driven
development using `zope.schema <http://docs.zope.org/zope.schema/>`_.

Installation
============

Installing nti.schema is easy::

  pip install nti.schema

nti.schema runs on Python 2 and Python 3, and CPython and PyPy.

Overview
========

Some of the most useful features include:

- :func:`~nti.schema.interfaces.find_most_derived_interface` for finding a
  bounded interface.
- :func:`~nti.schema.eqhash.EqHash` is a class-decorator for creating
  efficient, correct implementations of equality and hashing.
- :mod:`nti.schema.field` contains various schema fields, including a
  :class:`~nti.schema.field.Variant` type and more flexible collection types, all of which
  produce better validation errors.
- :mod:`nti.schema.fieldproperty` contains field properties that can
  adapt to interfaces or decode incoming text. The function
  :func:`~.createDirectFieldProperties` can assign just the necessary
  properties automatically.

.. toctree::

   interfaces
   schema
   fieldproperty
   field
   jsonschema
   subscribers
   vocabulary
   eqhash
   changelog
