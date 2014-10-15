#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Vocabularies and factories for use in schema fields,

$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component

from zope.schema.vocabulary import SimpleTerm as _SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary as _SimpleVocabulary
try:
	from plone.i18n.locales.interfaces import ICountryAvailability as _ICountryAvailability
except ImportError:
	_ICountryAvailability = None

class CountryTerm(_SimpleTerm):
	"""
	A titled, tokenized term representing a country. The
	token is the ISO3166 country code. The ``flag`` value is a
	browserresource path to an icon representing the country.
	"""

	def __init__( self, *args, **kwargs ):
		self.flag = kwargs.pop( 'flag', None )
		super(CountryTerm,self).__init__( *args, **kwargs )

	@classmethod
	def fromItem( cls, item ):
		token, cdata = item
		value = cdata['name']
		title = value
		flag = cdata['flag']

		return cls( value, token, title, flag=flag )


	def toExternalObject( self ):
		return { 'token': self.token,
				 'title': self.title,
				 'value': self.value,
				 'flag': self.flag }

class _CountryVocabulary(_SimpleVocabulary):
	"""
	__contains__ is based on the token, not the value.
	"""

	def __contains__( self, token ):
		return token in self.by_token

def CountryVocabularyFactory( context ):
	"""
	A vocabulary factory, if plone.i18n is available.
	"""
	countries = component.getUtility( _ICountryAvailability )
	return _CountryVocabulary( [CountryTerm.fromItem( item ) for item in countries.getCountries().items()] )
