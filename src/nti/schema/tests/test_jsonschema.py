#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for jsonschema.py
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# stdlib imports
import unittest

from zope.interface import Interface
from zope.interface import Attribute

from .. import jsonschema
from ..field import DecodingValidTextLine
from ..field import ListOrTuple
from ..field import Dict
from ..field import List
from ..field import Real
from ..field import Rational
from ..field import Complex
from ..field import Integral

# ABCs
from ..field import Sequence
from ..field import IndexedIterable
from ..field import MutableSequence

from ..field import Mapping
from ..field import MutableMapping


from hamcrest import assert_that
from hamcrest import has_entry
from hamcrest import is_
from hamcrest import has_length


__docformat__ = "restructuredtext en"


#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904,inherit-non-class,no-method-argument

class TestJsonSchemafier(unittest.TestCase):

    def test_excludes(self):

        class IA(Interface):

            def method():
                "A method"

            _thing = Attribute("A private attribute")

            hidden = Attribute("Hidden attribute")
            hidden.setTaggedValue(jsonschema.TAG_HIDDEN_IN_UI, True)

        schema = jsonschema.JsonSchemafier(IA).make_schema()
        assert_that(schema, is_({}))

    def test_readonly_override(self):
        class IA(Interface):

            field = Attribute("A field")

        schema = jsonschema.JsonSchemafier(IA, readonly_override=True).make_schema()
        assert_that(schema, has_entry('field', has_entry('readonly', True)))

    def test_ui_type(self):
        class IA(Interface):

            field = Attribute("A field")
            field.setTaggedValue(jsonschema.TAG_UI_TYPE, 'MyType')

        schema = jsonschema.JsonSchemafier(IA).make_schema()
        assert_that(schema, has_entry('field', has_entry('type', 'MyType')))

    def test_type_from_types(self):
        from zope.schema import Object
        from nti.schema.field import Variant

        class TranslateTestSchema(jsonschema.JsonSchemafier):

            def _translate(self, text):
                return text + self.context

        def _assert_type(t, name='field',
                         **kwargs):
            schema = TranslateTestSchema(IA, context=' TEST').make_schema()
            assert_that(schema, has_entry(name, has_entry('type', t)))
            for nested_name, matcher in kwargs.items():
                assert_that(schema, has_entry(name, has_entry(nested_name, matcher)))

            return schema

        class IUnderlyingA(Interface):

            text_field = DecodingValidTextLine(title=u'nested text',
                                               min_length=5)

        class IUnderlyingB(Interface):

            int_field = Integral()

        class IA(Interface):

            field = Attribute("A field")

            field2 = DecodingValidTextLine(title=u'A title',
                                           description=u'A description')

            list_field = List(DecodingValidTextLine())
            list_or_tuple_field = ListOrTuple(Real())
            dict_field = Dict(DecodingValidTextLine(), Real())
            mapping_field = Mapping()
            mmapping_field = MutableMapping()
            sequence_field = Sequence()
            msequence_field = MutableSequence()
            iiterable_field = IndexedIterable()

            real_field = Real()
            rational_field = Rational()
            complex_field = Complex()
            integral_field = Integral()

            object_field = Object(IUnderlyingA, required=True)
            variant_field = Variant([Object(IUnderlyingA), Object(IUnderlyingB)])

        IA['field']._type = str
        _assert_type('string')

        IA['field']._type = (str,)
        _assert_type('string')


        IA['field']._type = float
        _assert_type('float')

        IA['field']._type = (float,)
        _assert_type('float')

        IA['field']._type = int
        _assert_type('int')

        IA['field']._type = (int,)
        _assert_type('int')

        IA['field']._type = bool
        _assert_type('bool')

        _assert_type('string', 'field2',
                     base_type='string',
                     title=u'A title TEST',
                     description=u'A description TEST')

        _assert_type('list', 'list_field', value_type=has_entry('type', 'string'))
        _assert_type('list', 'list_or_tuple_field')
        _assert_type('list', 'sequence_field')
        _assert_type('list', 'msequence_field')
        _assert_type('list', 'iiterable_field')

        _assert_type('dict', 'dict_field',
                     key_type=has_entry('type', 'string'),
                     value_type=has_entry('type', 'Real'))
        _assert_type('dict', 'mapping_field')
        _assert_type('dict', 'mmapping_field')

        _assert_type('Real', 'real_field', base_type='float')
        _assert_type('Rational', 'rational_field', base_type='float')
        _assert_type('Complex', 'complex_field', base_type='float')
        _assert_type('Integral', 'integral_field', base_type='int')

        _assert_type('Object', 'object_field',
                     value_schema=has_entry('text_field', has_entry('min_length', 5)))

        schema = _assert_type('Variant', 'variant_field',
                              value_type_options=has_length(2))
        variant_schema_values = schema['variant_field']['value_type_options']
        assert_that(variant_schema_values[0], has_entry('type', 'Object'))
