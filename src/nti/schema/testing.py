#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test support for schemas and interfaces, mostly in the form of Hamcrest matchers.

.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)


from hamcrest.core.base_matcher import BaseMatcher
from hamcrest import all_of


from zope import interface
from zope.interface.verify import verifyObject
from zope.interface.exceptions import Invalid, BrokenImplementation, BrokenMethodImplementation, DoesNotImplement
from zope.schema import getValidationErrors, ValidationError

class Provides(BaseMatcher):

	def __init__( self, iface ):
		super(Provides,self).__init__( )
		self.iface = iface

	def _matches( self, item ):
		return self.iface.providedBy( item )

	def describe_to( self, description ):
		description.append_text( 'object providing') \
								 .append( str(self.iface) )

	def __repr__( self ):
		return 'object providing' + str(self.iface)

def provides( iface ):
	"""Matches if the object provides the given interface."""
	return Provides( iface )

class VerifyProvides(BaseMatcher):

	def __init__( self, iface ):
		super(VerifyProvides,self).__init__()
		self.iface = iface

	def _matches( self, item ):
		try:
			verifyObject(self.iface, item )
		except Invalid:
			return False
		else:
			return True

	def describe_to( self, description ):
		description.append_text( 'object verifiably providing ' ).append( str(self.iface.__name__) )

	def describe_mismatch( self, item, mismatch_description ):
		x = None
		mismatch_description.append_text( str(type(item))  )
		try:
			verifyObject( self.iface, item )
		except BrokenMethodImplementation as x:
			mismatch_description.append_text( str(x).replace( '\n', '' ) )
		except BrokenImplementation as x:
			mismatch_description.append_text( ' failed to provide attribute "').append_text( x.name ).append_text( '"' ).append_text( ' from ' ).append_text( self.iface[x.name].interface.getName() )
		except DoesNotImplement as x:
			mismatch_description.append_text( " does not implement the interface; it does implement " ).append_text( str(list(interface.providedBy(item))) )
		except Invalid as x:
			#mismatch_description.append_description_of( item ).append_text( ' has no attr ').append_text( self.attr )
			mismatch_description.append_text( str(x).replace( '\n', '' ) )


def verifiably_provides(*ifaces):
	"""
	Matches if the object verifiably provides the correct interface(s).
	NOTE: This does NOT test schema validity compliance.
	"""
	if len(ifaces) == 1:
		return VerifyProvides(ifaces[0])

	return all_of( *[VerifyProvides(x) for x in ifaces] )

class VerifyValidSchema(BaseMatcher):
	def __init__( self, iface ):
		super(VerifyValidSchema,self).__init__()
		self.iface = iface

	def _matches( self, item ):
		errors = getValidationErrors( self.iface, item )
		return not errors

	def describe_to( self, description ):
		description.append_text( 'object validly providing ' ).append( str(self.iface) )

	def describe_mismatch( self, item, mismatch_description ):
		x = None
		mismatch_description.append_text( str(type(item))  )


		errors = getValidationErrors( self.iface, item )

		for attr, exc in errors:
			try:
				raise exc
			except ValidationError:
				mismatch_description.append_text( ' has attribute "').append_text( attr ).append_text( '" with error "' ).append_text( repr(exc) ).append_text( '"\n\t ' )
			except Invalid as x:
				#mismatch_description.append_description_of( item ).append_text( ' has no attr ').append_text( self.attr )
				mismatch_description.append_text( str(x).replace( '\n', '' ) )

def validly_provides(*ifaces):
	"Matches if the object verifiably and validly provides the given schema (interface)"
	if len(ifaces) == 1:
		the_schema = ifaces[0]
		return all_of( verifiably_provides( the_schema ), VerifyValidSchema(the_schema) )

	prov = verifiably_provides(*ifaces)
	valid = [VerifyValidSchema(x) for x in ifaces]

	return all_of( prov, *valid )

class Implements(BaseMatcher):

	def __init__( self, iface ):
		super(Implements,self).__init__( )
		self.iface = iface

	def _matches( self, item ):
		return self.iface.implementedBy( item )

	def describe_to( self, description ):
		description.append_text( 'object implementing') \
								 .append( self.iface )

def implements( iface ):
	"""Matches if the object implements the interface"""
	return Implements( iface )


class ValidatedBy(BaseMatcher):

	def __init__( self, field ):
		super(ValidatedBy,self).__init__()
		self.field = field

	def _matches( self, data ):
		try:
			self.field.validate( data )
		except Exception:
			return False
		else:
			return True

	def describe_to( self, description ):
		description.append_text( 'data validated by' ).append( repr(self.field) )

	def describe_mismatch( self, item, mismatch_description ):
		ex = None
		try:
			self.field.validate( item )
		except Exception as e:
			ex = e

		mismatch_description.append_text( repr( self.field ) ).append_text( ' failed to validate ' ).append_text( repr( item ) ).append_text( ' with ' ).append_text( repr( ex ) )


def validated_by( field ):
	""" Matches if the data is validated by the given IField """
	return ValidatedBy( field )
from hamcrest import is_not
def not_validated_by( field ):
	""" Matches if the data is NOT validated by the given IField. """
	return is_not( validated_by( field ) )
