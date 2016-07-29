#!/usr/bin/env python

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import is_not
from hamcrest import has_item
from hamcrest import not_none
from hamcrest import contains
from hamcrest import has_entry
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import has_property
does_not = is_not

import unittest

from zope import interface



from dolmen.builtins import IUnicode

from nti.schema.field import Number
from nti.schema.field import Object


from nti.schema.field import DictFromObject
from nti.schema.field import ValidTextLine as TextLine



from nti.schema.interfaces import IBeforeDictAssignedEvent

from nti.schema.jsonschema import JsonSchemafier


class TestMisc(unittest.TestCase):

    def test_fixup_name(self):
        from zope.schema.fieldproperty import FieldPropertyStoredThroughField

        field = Object(IUnicode)
        field.__name__ = 'field'

        field_property = FieldPropertyStoredThroughField(field)
        field = field_property.field

        assert_that(field, has_property('__name__', '__st_field_st'))
        assert_that(field, has_property('__fixup_name__', 'field'))

from . import SchemaLayer
from zope.component import eventtesting


class TestConfigured(unittest.TestCase):

    layer = SchemaLayer


    def test_dict(self):

        dict_field = DictFromObject(key_type=TextLine(), value_type=Number())
        dict_field.__name__ = 'dict'

        class X(object):
            pass

        x = X()
        dict_field.set(x, dict_field.fromObject({'k': '1'}))

        assert_that(x, has_property('dict', {'k': 1.0}))

        events = eventtesting.getEvents(IBeforeDictAssignedEvent)
        assert_that(events, has_length(1))
        assert_that(events, contains(has_property('object', {'k': 1.0})))

    def test_country_vocabulary(self):
        from zope.schema import Choice

        class IA(interface.Interface):
            choice = Choice(title="Choice",
                            vocabulary="Countries")

        o = object()

        choice = IA['choice'].bind(o)
        assert_that(choice.vocabulary, is_(not_none()))
        term = choice.vocabulary.getTermByToken('us')
        assert_that(term, has_property('value', "United States"))
        ext = term.toExternalObject()
        assert_that(ext, has_entry('flag', u'/++resource++country-flags/us.gif'))
        assert_that(ext, has_entry('title', 'United States'))

        schema = JsonSchemafier(IA).make_schema()
        assert_that(schema, has_entry('choice', has_entry('choices', has_item(ext))))



from nti.schema.schema import _superhash as superhash

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
                        ((1, 1),
                         (2, (1, 2, 3)),
                         (3, ((4, (4, 5, 6)),)))
                    ))

        assert_that(hash(superhash(d)),
                    is_(-6213620179105025536))
