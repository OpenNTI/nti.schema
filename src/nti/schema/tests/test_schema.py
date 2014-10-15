#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import assert_that
from hamcrest import is_
from hamcrest import has_property
from hamcrest import has_length
from hamcrest import contains
from hamcrest import has_key
from hamcrest import calling
from hamcrest import raises
from hamcrest import none
from hamcrest import is_not
from hamcrest import not_none
from hamcrest import has_entry
from hamcrest import has_item
import unittest
does_not = is_not

from nti.schema.testing import verifiably_provides, validated_by, not_validated_by


from ..field import HTTPURL, Variant, ObjectLen, Object
#from ..schema import DataURI
from ..interfaces import IVariant
from ..field import Number
from ..field import DictFromObject
from ..field import ListOrTuple
from ..field import ValidRegularExpression
from ..field import ValidTextLine as TextLine
from ..interfaces import IBeforeSequenceAssignedEvent
from ..interfaces import IBeforeDictAssignedEvent
from ..fieldproperty import createFieldProperties
from ..fieldproperty import createDirectFieldProperties

from ..jsonschema import JsonSchemafier

from dolmen.builtins import IUnicode
from zope import interface
from zope.interface.common import interfaces as cmn_interfaces

from zope.schema import interfaces as sch_interfaces
from zope.schema import Dict
from zope.schema.interfaces import InvalidURI

class TestMisc(unittest.TestCase):


	def test_objectlen(self):
		# If we have the inheritance messed up, we will have problems
		# creating, or we will have problems validating one part or the other.

		olen = ObjectLen( IUnicode, max_length=5 ) # default val for min_length

		olen.validate( 'a' )
		olen.validate( '' )

		assert_that( calling(olen.validate).with_args(object()),
					 raises(sch_interfaces.SchemaNotProvided))

		assert_that( calling(olen.validate).with_args('abcdef'),
					 raises(sch_interfaces.TooLong) )


	def test_create_direct_field_properties(self):
		class IA(interface.Interface):
			a = TextLine(title="a")

		class IB(IA):
			b = TextLine(title="b")

		class A(object):
			createFieldProperties(IA)

		class B(object):
			createDirectFieldProperties(IB)

		assert_that( A.__dict__, has_key( 'a' ) )
		assert_that( B.__dict__, has_key( 'b' ) )
		assert_that( B.__dict__, does_not( has_key( 'a' ) ) )
		# And nothing extra crept in, just the four standard things
		# __dict__, __doct__, __module__, __weakref__, and b
		assert_that( B.__dict__, has_length( 5 ) )


	def test_http_url(self):

		http = HTTPURL(__name__='foo')

		assert_that( http.fromUnicode( 'www.google.com' ),
					 is_( 'http://www.google.com' ) )

		assert_that( http.fromUnicode( 'https://www.yahoo.com' ),
					 is_( 'https://www.yahoo.com' ) )

		try:
			http.fromUnicode( 'mailto:jason@nextthought.com' )
			self.fail("Must raise")
		except InvalidURI as ex:
			exception = ex


		assert_that( exception, has_property( 'field', http ) )
		assert_that( exception, has_property( 'value', 'mailto:jason@nextthought.com' ) )
		assert_that( exception, has_property( 'message', 'The specified URI is not valid.' ) )

	# def test_data_uri():
	# 	from .test_dataurl import GIF_DATAURL
	# 	field = DataURI(__name__='foo')

	# 	url = field.fromUnicode(GIF_DATAURL)

	# 	assert_that( url, has_property( 'mimeType', 'image/gif') )
	# 	assert_that( url, has_property( 'data', is_not( none() ) ) )

	def test_regex(self):
		field = ValidRegularExpression('[bankai|shikai]', flags=0)
		assert_that(field.constraint("bankai"), is_(True))
		assert_that(field.constraint("shikai"), is_(True))
		assert_that(field.constraint("Shikai"), is_(False))
		assert_that(field.constraint("foo"), is_(False))
		field = ValidRegularExpression('[bankai|shikai]')
		assert_that(field.constraint("Shikai"), is_(True))
		assert_that(field.constraint("banKAI"), is_(True))

	def test_variant(self):

		syntax_or_lookup = Variant( (Object(cmn_interfaces.ISyntaxError),Object(cmn_interfaces.ILookupError), Object(IUnicode)) )

		assert_that( syntax_or_lookup, verifiably_provides( IVariant ) )

		# validates
		assert_that( SyntaxError(), validated_by( syntax_or_lookup ) )
		assert_that( LookupError(), validated_by( syntax_or_lookup ) )

		# doesn't validate
		assert_that( b'foo', not_validated_by( syntax_or_lookup ) )

		assert_that( syntax_or_lookup.fromObject( 'foo' ), is_( 'foo' ) )

		assert_that( calling( syntax_or_lookup.fromObject).with_args(object()),
					 raises(TypeError) )


		# cover
		syntax_or_lookup.getDoc()

	def test_complex_variant(self):

		dict_field = Dict( key_type=TextLine(), value_type=TextLine() )
		string_field = Object(IUnicode)
		list_of_numbers_field = ListOrTuple( value_type=Number() )

		variant = Variant( (dict_field, string_field, list_of_numbers_field) )
		variant.getDoc() # cover
		# It takes all these things
		for d in { 'k': 'v'}, 'foo', [1, 2, 3]:
			assert_that( d, validated_by( variant ) )

		# It rejects these
		for d in {'k': 1}, b'foo', [1, 2, 'b']:
			assert_that( d, not_validated_by( variant ) )


		# A name set now is reflected down the line
		variant.__name__ = 'baz'
		for f in variant.fields:
			assert_that( f, has_property( '__name__', 'baz' ) )

		# and in clones
		clone = variant.bind( object() )
		for f in clone.fields:
			assert_that( f, has_property( '__name__', 'baz' ) )

		# which doesn't change the original
		clone.__name__ = 'biz'
		for f in clone.fields:
			assert_that( f, has_property( '__name__', 'biz' ) )
		for f in variant.fields:
			assert_that( f, has_property( '__name__', 'baz' ) )


		# new objects work too
		new = Variant( variant.fields, __name__='boo' )
		for f in new.fields:
			assert_that( f, has_property( '__name__', 'boo' ) )

from zope.component import eventtesting
from zope.testing import cleanup

from . import ZopeComponentLayer
from . import ConfiguringLayerMixin

class SchemaLayer(ZopeComponentLayer,
				  ConfiguringLayerMixin):

	set_up_packages = ('nti.schema',)

	@classmethod
	def setUp(cls):
		cls.setUpPackages()

	@classmethod
	def tearDown(cls):
		cls.tearDownPackages()
		cleanup.cleanUp()

	@classmethod
	def testSetUp(cls, test=None):
		pass

	testTearDown = testSetUp

class TestConfigured(unittest.TestCase):
	layer = SchemaLayer


	def test_nested_variants(self):
		# Use case: Chat messages are either a Dict, or a Note-like body, which itself is a list of variants

		dict_field = Dict( key_type=TextLine(), value_type=TextLine() )

		string_field = Object(IUnicode)
		number_field = Number()
		list_of_strings_or_numbers = ListOrTuple( value_type=Variant( (string_field, number_field) ) )

		assert_that( [1, '2'], validated_by( list_of_strings_or_numbers ) )
		assert_that( {'k': 'v'}, validated_by( dict_field ) )

		dict_or_list = Variant( ( dict_field, list_of_strings_or_numbers ) )

		assert_that( [1, '2'], validated_by( dict_or_list ) )
		assert_that( {'k': 'v'}, validated_by( dict_or_list ) )


		class X(object):
			pass
		x = X()
		dict_or_list.set( x, [1, '2'] )

		events = eventtesting.getEvents( IBeforeSequenceAssignedEvent )
		assert_that( events, has_length( 1 ) )
		assert_that( events, contains( has_property( 'object', [1, '2'] ) ) )

		eventtesting.clearEvents()

		dict_or_list.set( x, {'k': 'v'} )
		events = eventtesting.getEvents( IBeforeDictAssignedEvent )
		assert_that( events, has_length( 1 ) )
		assert_that( events, contains( has_property( 'object', {'k': 'v'} ) ) )

	def test_dict(self):

		dict_field = DictFromObject( key_type=TextLine(), value_type=Number() )
		dict_field.__name__ = 'dict'

		class X(object):
			pass
		x = X()
		dict_field.set( x, dict_field.fromObject({'k': '1'}) )

		assert_that( x, has_property('dict', {'k': 1.0} ))

		events = eventtesting.getEvents( IBeforeDictAssignedEvent )
		assert_that( events, has_length( 1 ) )
		assert_that( events, contains( has_property( 'object', {'k': 1.0} ) ) )



	def test_country_vocabulary(self):
		from zope.schema import Choice
		class IA(interface.Interface):
			choice = Choice(title="Choice",
							vocabulary="Countries")

		o = object()

		choice = IA['choice'].bind( o )
		assert_that( choice.vocabulary, is_( not_none() ) )
		term = choice.vocabulary.getTermByToken( 'us' )
		assert_that( term, has_property( 'value', "United States" ) )
		ext = term.toExternalObject()
		assert_that( ext, has_entry( 'flag', u'/++resource++country-flags/us.gif' ) )
		assert_that( ext, has_entry( 'title', 'United States'  ) )

		schema = JsonSchemafier( IA ).make_schema()
		assert_that( schema, has_entry( 'choice', has_entry( 'choices', has_item( ext ) ) ) )

try:
	from nti.testing.matchers import aq_inContextOf
	from ..fieldproperty import AcquisitionFieldProperty
	from Acquisition import Implicit
	from ExtensionClass import Base
except ImportError:
	pass
else:

	class TestAq(unittest.TestCase):

		def test_aq_property(self):

			class IBaz(interface.Interface):
				pass
			class IFoo(interface.Interface):
				ob = Object(IBaz)

			@interface.implementer(IBaz)
			class Baz(object):
				pass

			class BazAQ(Implicit,Baz):
				pass

			@interface.implementer(IFoo)
			class Foo(Base):
				ob = AcquisitionFieldProperty(IFoo['ob'])

			assert_that( Foo, has_property( 'ob', is_( AcquisitionFieldProperty ) ) )

			foo = Foo()
			assert_that( foo, has_property( 'ob', none() ) )

			foo.ob = Baz()
			assert_that( foo, has_property( 'ob', is_not( aq_inContextOf( foo ) ) ) )

			foo.ob = BazAQ()
			assert_that( foo, has_property( 'ob', aq_inContextOf( foo ) ) )


from ..schema import _superhash as superhash

class TestSuperHash(unittest.TestCase):

	def test_iterable(self):
		assert_that(hash(superhash([1, 3, 5])),
					is_(hash(superhash([x for x in [1, 3, 5]]))))

		assert_that(superhash([1, 2]), is_not(superhash([2, 1])))
		assert_that(hash(superhash([1, 2])), is_not(hash(superhash([2, 1]))))

	def test_nested_dict(self):
		d = {1: 1,
			 2: [1, 2, 3],
			 3: {4: [4, 5, 6]}}

		assert_that(superhash(d),
					is_(
						((1,1),
						 (2, (1, 2, 3)),
						 (3, ((4, (4, 5, 6)),)))
					))

		assert_that(hash(superhash(d)),
					is_(-6213620179105025536) )
