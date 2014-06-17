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




def EqHash(*names):
	"""
	A class decorator factory for the common pattern of writing
	``__eq__`` and ``__hash__`` methods that check the same
	list of attributes on a given object.

	Right now, you must pass as individual arguments the property
	names to check; in the future, you may be able to pass a schema
	interface that defines the property names.
	"""
	def _eq_hash(*names):
		# getter returns a tuple, which can be equality
		# checked and hashed
		getter = operator.attrgetter(*names)

		def __eq__(self, other):
			try:
				return self is other or (getter(self) == getter(other))
			except AttributeError:
				return NotImplemented

		seed = hash(names)
		def __hash__(self):
			h = seed
			h ^= hash(getter(self))
			return h

		return __eq__, __hash__

	def x(cls):
		__eq__, __hash__ = _eq_hash(*names)
		cls.__eq__ = __eq__
		cls.__hash__ = __hash__
		return cls
	return x
