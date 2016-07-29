#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Helpers for hashing and equality based on a list of names.

.. $Id$
"""

from __future__ import print_function,  absolute_import, division
__docformat__ = "restructuredtext en"


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

    Additional parameters are only available via keywords::

      @EqHash('a', 'b')
      class Thing(object):
         a = 'a'
         b = 'b'

      @EqHash('c', include_super=True)
      class ChildThing(Thing):
         c = 'c'

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

    _include_super = kwargs.pop('include_super', False)
    superhash = kwargs.pop("superhash", False)
    _include_type = kwargs.pop('include_type', False)

    if kwargs:
        raise TypeError("Unexpected keyword args", kwargs)
    if not names and not _include_super and not _include_type:
        raise TypeError("Asking to hash/eq nothing, but not including super or type")


    def x(cls):
        __eq__, __hash__, __ne__ = _eq_hash(cls, names,
                                            _include_super, _include_type, superhash)
        cls.__eq__ = __eq__
        cls.__hash__ = __hash__
        cls.__ne__ = __ne__
        return cls
    return x

def _eq_hash(cls, names, include_super, include_type, superhash): # pylint:disable=I0011,W0622,R0912
    names = tuple((str(x) for x in names)) # make sure they're native strings, not unicode on Py2
    # We assume the class hierarchy of these objects does not change
    if include_super:
        superclass = cls.__mro__[1]
        superclass_eq = superclass.__eq__
        superclass_hash = superclass.__hash__

    # 1 and 0 are constants and faster to load than the globals True/False
    # (in python 2)

    def __eq__(self, other):
        if self is other:
            return 1

        if include_type:
            if not isinstance(other, cls):
                return 0

        if include_super:
            s = superclass_eq(self, other)
            if s is NotImplemented or not s:
                return s


        # We take these one at a time (rather than using
        # operator.attrgetter). In the cases where some attributes
        # are computed, this can be more efficient if we discover
        # a mismatch early. Also, it lets us easily distinguish
        # between an AttributeError on self (which is a
        # programming error in calling EqHash) or the other object
        _ga = getattr # load_fast in the loop
        for name in names:
            my_val = _ga(self, name)
            try:
                other_val =_ga(other, name)
            except AttributeError:
                return NotImplemented
            else:
                # Amusingly, even though this does
                # more push/pop than inlining in the
                # body of the try block, it benchmarks
                # faster
                if my_val != other_val:
                    return 0
        return 1

    def __ne__(self, other):
        eq = __eq__(self, other)
        if eq is NotImplemented:
            return eq
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
            h ^= superclass_hash(self) << 2

        # If we or-equal for every attribute separately, we
        # easily run the risk of saturating the integer. So we boil
        # all attributes down to one value to hash
        if names:
            ga = getattr
            h ^= _hash( [ga(self, name) for name in names] )
        return h

    return __eq__, __hash__, __ne__
