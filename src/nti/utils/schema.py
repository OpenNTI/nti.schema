#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utility classes and methods for working with zope schemas.

Also patches a bug in the :class:`dm.zope.schema.schema.Object` class
that requires the default value for ``check_declaration`` to be specified;
thus always import `Object` from this module

$Id$
"""
from __future__ import print_function, unicode_literals
from . import MessageFactory as _
from dm.zope.schema.schema import SchemaConfigured, schemadict, Object

class PermissiveSchemaConfigured(SchemaConfigured):
	"""
	A mixin subclass of :class:`SchemaConfigured` that allows
	for extra keywords (those not defined in the schema) to silently be ignored.
	This is an aid to evolution of code and con be helpful in testing.

	To allow for one-by-one conversions and updates, this class defines an attribute
	``SC_PERMISSIVE``, defaulting to True, that controls this behaviour.
	"""

	SC_PERMISSIVE = True

	def __init__( self, **kwargs ):
		if not self.SC_PERMISSIVE:
			super(PermissiveSchemaConfigured,self).__init__( **kwargs )
		else:
			schema = schemadict(self.sc_schema_spec())
			for k in kwargs.keys():
				if k not in schema:
					kwargs.pop( k )
			super(PermissiveSchemaConfigured,self).__init__( **kwargs )

Object.check_declaration = True

from zope import interface
from zope import schema
from zope import component
from zope.component import handle
from zope.event import notify
from zope.schema import interfaces as sch_interfaces
import numbers

class Number(schema.Float):
	"""
	A field that parses like a float from a string, but accepts any number.
	"""
	_type = numbers.Number

class InvalidValue(sch_interfaces.InvalidValue):
	"""
	Adds a field specifically to carry the value that is invalid.
	"""
	value = None

	def __init__( self, *args, **kwargs ):
		super(InvalidValue,self).__init__( *args )
		if 'value' in kwargs:
			self.value = kwargs['value']
		if 'field' in kwargs:
			self.field = kwargs['field']

# And we monkey patch it in to InvalidValue as well
if not hasattr(sch_interfaces.InvalidValue, 'value' ):
	setattr( sch_interfaces.InvalidValue, 'value', None )

# And give all validation errors a 'field'
if not hasattr(sch_interfaces.ValidationError, 'field' ):
	setattr( sch_interfaces.ValidationError, 'field', None )

class FieldValidationMixin(object):
	"""
	A field mixin that causes slightly better errors to be created.
	"""

	def _fixup_validation_error_args( self, e, value ):
		# Called when the exception has one argument, which is usually, thought not always,
		# the message
		e.args = (value, e.args[0], self.__name__)

	def _reraise_validation_error(self, e, value, _raise=False):
		if len(e.args) == 1: # typically the message is the only thing
			self._fixup_validation_error_args( e, value )
		elif isinstance( e, sch_interfaces.TooShort ) and len(e.args) == 2:
			# Note we're capitalizing the field in the message.
			e.i18n_message = _('${field} is too short.', mapping={'field': self.__name__.capitalize(), 'minLength': e.args[1]})
			e.args = ( self.__name__.capitalize() + ' is too short.',
					   self.__name__,
					   value )
		e.field = self
		if not getattr( e, 'value', None):
			e.value  = value
		if _raise:
			raise e
		raise

	def _validate(self, value):
		try:
			super(FieldValidationMixin,self)._validate( value )
		except sch_interfaces.ValidationError as e:
			self._reraise_validation_error( e, value )


from zope.schema._field import BeforeObjectAssignedEvent

class ValidTextLine(FieldValidationMixin,schema.TextLine):
	"""
	A text line that produces slightly better error messages. They will all
	have the 'field' property.

	We also fire BeforeObjectAssignedEvents, which the normal
	mechanism does not.
	"""

	def set( self, object, value ):
		try:
			event = BeforeObjectAssignedEvent(value, self.__name__, object)
			notify(event)
			value = event.object
			super(ValidTextLine,self).set( object, value )
		except sch_interfaces.ValidationError as e:
			self._reraise_validation_error( e, value )

class DecodingValidTextLine(ValidTextLine):
	"""
	A text type that will attempt to decode non-unicode
	data as UTF-8.
	"""

	def fromUnicode( self, value ):
		if not isinstance( value, self._type ):
			value = value.decode( 'utf-8' ) # let raise UnicodeDecodeError
		super(DecodingValidTextLine,self).fromUnicode( value )

class HTTPURL(FieldValidationMixin,schema.URI):
	"""
	A URI field that ensures and requires its value to be an absolute
	HTTP/S URL.
	"""

	def _fixup_validation_error_args( self, e, value ):
		if isinstance( e, sch_interfaces.InvalidURI ):
			# This class differs by using the value as the argument, not
			# a message
			e.args = ( value, e.__doc__, self.__name__ )
			e.message = e.i18n_message = e.__doc__
		else:
			super(HTTPURL,self)._fixup_validation_error_args( e, value )

	def fromUnicode( self, value ):
		# This can wind up producing something invalid if an
		# absolute URI was already given for mailto: for whatever.
		# None of the regexs (zopes or grubers) flag that as invalid.
		# so we try to
		orig_value = value
		if value:
			lower = value.lower()
			if not lower.startswith( 'http://' ) and not lower.startswith( 'https://' ):
				# assume http
				value = 'http://' + value
		result = super(HTTPURL,self).fromUnicode( value )
		if result.count( ':' ) != 1:
			self._reraise_validation_error( sch_interfaces.InvalidURI( orig_value ), orig_value, _raise=True )

		return result

class IndexedIterable(schema.List):
	"""
	An arbitrary (indexable) iterable, not necessarily a list or tuple;
	either of those would be acceptable at any time.
	The values may be homogeneous by setting the value_type
	"""
	_type = None # Override from super to not force a list

class UniqueIterable(schema.Set):
	"""
	An arbitrary iterable, not necessarily an actual :class:`set` object and
	not necessarily iterable, but one whose contents are unique.
	"""
	_type = None # Override to not force a set

def find_most_derived_interface( ext_self, iface_upper_bound, possibilities=None ):
	"""
	Search for the most derived version of the interface `iface_upper_bound`
	implemented by `ext_self` and return that. Always returns at least `iface_upper_bound`
	:param possibilities: An iterable of schemas to consider
	"""
	if possibilities is None:
		possibilities = interface.providedBy( ext_self )
	_iface = iface_upper_bound
	for iface in possibilities:
		if iface.isOrExtends( _iface ):
			_iface = iface
	return _iface

@component.adapter(sch_interfaces.IBeforeObjectAssignedEvent)
def before_object_assigned_event_dispatcher(event):
	"""
	Listens for :mod:`zope.schema` to fire :class:`zope.schema.interfaces.IBeforeObjectAssignedEvent`,
	and re-dispatches these events based on the value being assigned, the object being assigned to,
	and of course the event.

	This is analogous to :func:`zope.component.event.objectEventNotify`
	"""

	handle( event.object, event.context, event )
