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

        def _assert_type(t, name='field', base_type=None):
            schema = jsonschema.JsonSchemafier(IA).make_schema()
            assert_that(schema, has_entry(name, has_entry('type', t)))
            if base_type:
                assert_that(schema, has_entry(name, has_entry('base_type', base_type)))
            return schema

        class IA(Interface):

            field = Attribute("A field")

            field2 = DecodingValidTextLine()

            list_field = List()
            list_or_tuple_field = ListOrTuple()
            dict_field = Dict()
            mapping_field = Mapping()
            mmapping_field = MutableMapping()
            sequence_field = Sequence()
            msequence_field = MutableSequence()
            iiterable_field = IndexedIterable()

            real_field = Real()
            rational_field = Rational()
            complex_field = Complex()
            integral_field = Integral()

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

        schema = _assert_type('string', 'field2')
        assert_that(schema, has_entry('field2', has_entry('base_type', 'string')))

        _assert_type('list', 'list_field')
        _assert_type('list', 'list_or_tuple_field')
        _assert_type('list', 'sequence_field')
        _assert_type('list', 'msequence_field')
        _assert_type('list', 'iiterable_field')

        _assert_type('dict', 'dict_field')
        _assert_type('dict', 'mapping_field')
        _assert_type('dict', 'mmapping_field')

        _assert_type('Real', 'real_field', 'float')
        _assert_type('Rational', 'rational_field', 'float')
        _assert_type('Complex', 'complex_field', 'float')
        _assert_type('Integral', 'integral_field', 'int')
