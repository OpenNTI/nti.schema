#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Helpers for writing code that implements schemas.

$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)


from dm.zope.schema.schema import SchemaConfigured, schemadict, Object as ObjectBase
ObjectBase.check_declaration = True

import operator

class PermissiveSchemaConfigured(SchemaConfigured):
	"""
	A mixin subclass of :class:`SchemaConfigured` that allows
	for extra keywords (those not defined in the schema) to silently be ignored.
	This is an aid to evolution of code and can be helpful in testing.

	To allow for one-by-one conversions and updates, this class defines an attribute
	``SC_PERMISSIVE``, defaulting to True, that controls this behaviour.
	"""

	SC_PERMISSIVE = True

	def __init__( self, **kwargs ):
		if not self.SC_PERMISSIVE:
			super(PermissiveSchemaConfigured,self).__init__( **kwargs )
		else:
			_schema = schemadict(self.sc_schema_spec())
			for k in kwargs.keys():
				if k not in _schema:
					kwargs.pop( k )
			super(PermissiveSchemaConfigured,self).__init__( **kwargs )


def _superhash(value):
	"""
	Returns something that's hashable, either the value itself,
	or a tuple that can in turn be hashed
	"""
	try:
		# By returning the original value, if it was hashable,
		# we may get better ultimate hash results;
		# the cost is hashing that value twice
		hash(value)
	except TypeError:
		# Dict?
		try:
			# Sort these, they have no order
			items = sorted(value.items())
		except AttributeError:
			# mutable iterable, which we must not sort
			items = value

		return tuple([_superhash(item)
					  for item
					  in items])
	else:
		return value

def EqHash(*names,
		   **kwargs):
	"""
	A class decorator factory for the common pattern of writing
	``__eq__``/``__ne__`` and ``__hash__`` methods that check the same
	list of attributes on a given object.

	Right now, you must pass as individual arguments the property
	names to check; in the future, you may be able to pass a schema
	interface that defines the property names. Property names are compared
	for equality in the order they are given, so place the cheapest first.

	:keyword include_super: If set to ``True`` (*not* the default)
		then the equality (and perhaps hash) values of super will be considered.
	:keyword superhash: If set to ``True`` (*not* the default),
		then the hash function will be made to support certain
		mutable types (lists and dictionaries) that ordinarily cannot
		be hashed. Use this only when those items are functionally
		treated as immutable.

	"""

	include_super = kwargs.pop('include_super', False)
	superhash = kwargs.pop("superhash", False)

	def _eq_hash(cls, *names):
		# getter returns a tuple, which can be equality
		# checked and hashed, if its members are
		getter = operator.attrgetter(*names)

		def __eq__(self, other):
			if self is other:
				return True

			if include_super:
				s = super(cls, self).__eq__(other)
				if s is NotImplemented or not s:
					return s

			try:
				# Rather than use the results of the getter,
				# we take these one at a time. In the cases where
				# some attributes are computed, this can be more efficient
				# if we discover a mismatch early
				for name in names:
					if getattr(self, name) != getattr(other, name):
						return False
				return True
			except AttributeError:
				return NotImplemented

		def __ne__(self, other):
			eq = __eq__(self, other)
			if eq is NotImplemented:
				return NotImplemented
			return not eq

		# Our contract for include_super says that hashing
		# may or may not be included. It shouldn't affect the results
		# if we do not actually include it, so we don't for simplicity
		# and speed
		seed = hash(names)

		if superhash:
			def _hash(values):
				# We're hashing the sequence of superhash values
				# for each value; we could probably do better?
				return hash( tuple([_superhash(x) for x in values]) )
		else:
			_hash = hash

		def __hash__(self):
			h = seed
			h ^= _hash(getter(self))
			return h

		return __eq__, __hash__, __ne__

	def x(cls):
		__eq__, __hash__, __ne__ = _eq_hash(cls, *names)
		cls.__eq__ = __eq__
		cls.__hash__ = __hash__
		cls.__ne__ = __ne__
		return cls
	return x
