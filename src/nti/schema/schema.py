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
	:keyword include_type: If set to ``True`` (*not* the default),
		equality will only be true if the other object is an instance
		of the class this is declared on. Use this only when there are
		a series of subclasses who differ in no attributes but should not
		compare equal to each other. Note that this can lead to violating
		the commutative property.

	"""

	include_super = kwargs.pop('include_super', False)
	superhash = kwargs.pop("superhash", False)
	include_type = kwargs.pop('include_type', False)

	if kwargs:
		raise TypeError("Unexpected keyword args", kwargs)
	if not names and not include_super and not include_type:
		raise TypeError("Asking to hash/eq nothing, but not including super or type")

	def _eq_hash(cls, *names):
		def __eq__(self, other):
			if self is other:
				return True

			if include_type:
				if not isinstance(other, cls):
					return False

			if include_super:
				s = super(cls, self).__eq__(other)
				if s is NotImplemented or not s:
					return s


			# We take these one at a time (rather than using
			# operator.attrgetter). In the cases where some attributes
			# are computed, this can be more efficient if we discover
			# a mismatch early. Also, it lets us easily distinguish
			# between an AttributeError on self (which is a
			# programming error in calling EqHash) or the other object
			for name in names:
				my_val = getattr(self, name)
				try:
					other_val = getattr(other, name)
				except AttributeError:
					return NotImplemented
				else:
					if my_val != other_val:
						return False
			return True


		def __ne__(self, other):
			eq = __eq__(self, other)
			if eq is NotImplemented:
				return NotImplemented
			return not eq

		# Our contract for include_super says that hashing
		# may or may not be included. It shouldn't affect the results
		# if we do not actually include it, unless there are no values
		# being hashed from this object. However, for consistency,
		# we always include it if asked
		seed = hash(names)

		if superhash:
			def _hash(values):
				# We're hashing the sequence of superhash values
				# for each value; we could probably do better?
				return hash( tuple([_superhash(x) for x in values]) )
		else:
			def _hash(values):
				return hash(tuple(values))

		def __hash__(self):
			h = seed
			if include_super:
				h ^= super(cls, self).__hash__() << 2

			# If we or-equal for every attribute separately, we
			# easily run the risk of saturating the integer. So we boil
			# all attributes down to one value to hash
			if names:
				h ^= _hash( [getattr(self, name) for name in names] )
			return h

		return __eq__, __hash__, __ne__

	def x(cls):
		__eq__, __hash__, __ne__ = _eq_hash(cls, *names)
		cls.__eq__ = __eq__
		cls.__hash__ = __hash__
		cls.__ne__ = __ne__
		return cls
	return x
