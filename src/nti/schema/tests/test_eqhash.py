#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""


.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904

import unittest
from hamcrest import assert_that
from hamcrest import is_
from hamcrest import is_not
from hamcrest import calling
from hamcrest import raises

from ..eqhash import EqHash
from nti.schema.schema import _superhash as superhash # make sure works

@EqHash('a', 'b')
class Thing(object):
    a = 'a'
    b = 'b'

@EqHash('a', 'b', superhash=True)
class Thing2(object):
    a = 'a'
    b = 'b'

@EqHash('a', 'b', include_type=True)
class NotThing(object):
    a = 'a'
    b = 'b'


@EqHash('c', include_super=True)
class ChildThing(Thing):
    c = 'c'

@EqHash('c', include_super=False)
class ChildThingNoSuper(Thing):
    c = 'c'

class TestEqHash(unittest.TestCase):

    def test_eq_hash(self):

        thing1 = Thing()
        thing2 = Thing()

        assert_that(thing1, is_(thing1)) # self
        assert_that(thing1, is_(thing2)) # commutative
        assert_that(thing2, is_(thing1))
        assert_that(hash(thing1), is_(hash(thing2)))

        assert_that(thing1, is_not(self)) # missing attr

        thing2.b = 'B'

        assert_that(thing1, is_not(thing2))
        assert_that(hash(thing1), is_not(hash(thing2)))

        # hamcrest calls == even for is_not
        assert thing1 != thing2
        assert thing1 != self # NotImplemented

    def test_eq_hash_classes(self):
        # Default doesn't include classes

        assert_that(Thing(), is_(Thing2()))
        assert_that(hash(Thing()), is_(hash(Thing2())))

        # We can ask for it, but note that the order of arguments
        # matters
        assert_that(Thing(), is_(NotThing()))
        assert_that(NotThing(), is_not(Thing()))

    def test_eq_hash_super(self):
        thing1 = ChildThing()
        thing2 = ChildThing()

        assert_that(thing1, is_(thing2))

        assert_that(hash(thing1), is_(hash(thing2)))

        thing1.a = 'A'
        assert_that(thing1, is_not(thing2))
        assert_that(hash(thing1), is_not(hash(thing2)))

    def test_eq_hash_no_super(self):
        thing1 = ChildThingNoSuper()
        thing2 = ChildThingNoSuper()

        assert_that(thing1, is_(thing2))
        assert_that(hash(thing1), is_(hash(thing2)))

        thing1.a = 'A'
        assert_that(thing1, is_(thing2))
        assert_that(hash(thing1), is_(hash(thing2)))

        thing1.c = 'C'
        assert_that(thing1, is_not(thing2))
        assert_that(hash(thing1), is_not(hash(thing2)))

    def test_bad_construct(self):
        assert_that(calling(EqHash), raises(TypeError, "Asking to hash"))
        assert_that(calling(EqHash).with_args(foo=True),
                    raises(TypeError, "Unexpected keyword"))



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
