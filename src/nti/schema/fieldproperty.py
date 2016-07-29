#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Computed attributes based on schema fields.

.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import sys

from zope import interface
from zope.schema import interfaces as sch_interfaces

# Re-export some things as part of our public API so we can
# later re-implement them locally if needed

from zope.schema.fieldproperty import FieldProperty
from zope.schema.fieldproperty import createFieldProperties
from zope.schema.fieldproperty import FieldPropertyStoredThroughField

try:
    from Acquisition import aq_base
    from Acquisition.interfaces import IAcquirer
except ImportError:
    class IAcquirer(interface.Interface):
        """
        Placeholder because Acquisition is not installed
        """
    def aq_base(o):
        return o

class AcquisitionFieldProperty(FieldProperty):
    """
    A field property that supports acquisition. Returned objects
    will be __of__ the instance, and set objects will always be the unwrapped
    base.
    """

    def __get__(self, instance, klass):
        result = super(AcquisitionFieldProperty, self).__get__(instance, klass)
        if instance is not None and IAcquirer.providedBy(result):  # even defaults get wrapped
            result = result.__of__(instance)
        return result

    def __set__(self, instance, value):
        super(AcquisitionFieldProperty, self).__set__(instance, aq_base(value))

class UnicodeConvertingFieldProperty(FieldProperty):
    """
    Accepts bytes input for the unicode property if it can be
    decoded as UTF-8. This is primarily to support legacy test cases
    and should be removed when all constants are unicode.
    """

    def __set__(self, inst, value):
        if value and not isinstance(value, unicode):
            value = value.decode('utf-8')
        super(UnicodeConvertingFieldProperty, self).__set__(inst, value)

class AdaptingFieldProperty(FieldProperty):
    """
    Primarily for legacy support and testing, adds adaptation to an interface
    when setting a field. This is most useful when the values are simple literals
    like strings.
    """

    def __init__(self, field, name=None):
        if not sch_interfaces.IObject.providedBy(field):
            raise sch_interfaces.WrongType("Don't know how to get schema from %s" % field)
        self.schema = field.schema

        super(AdaptingFieldProperty, self).__init__(field, name=name)

    def __set__(self, inst, value):
        try:
            super(AdaptingFieldProperty, self).__set__(inst, value)
        except sch_interfaces.SchemaNotProvided:
            super(AdaptingFieldProperty, self).__set__(inst, self.schema(value))

class AdaptingFieldPropertyStoredThroughField(FieldPropertyStoredThroughField):
    """
    Primarily for legacy support and testing, adds adaptation to an interface
    when setting a field. This is most useful when the values are simple literals
    like strings.
    """

    def __init__(self, field, name=None):
        if not sch_interfaces.IObject.providedBy(field):
            raise sch_interfaces.WrongType()
        self.schema = field.schema
        super(AdaptingFieldPropertyStoredThroughField, self).__init__(field, name=name)

    def __set__(self, inst, value):
        try:
            super(AdaptingFieldPropertyStoredThroughField, self).__set__(inst, value)
        except sch_interfaces.SchemaNotProvided:
            super(AdaptingFieldPropertyStoredThroughField, self).__set__(inst, self.schema(value))

def createDirectFieldProperties(__schema, omit=(), adapting=False):
    """
    Like :func:`zope.schema.fieldproperty.createFieldProperties`, except
    only creates properties for fields directly contained within the
    given schema; inherited fields from parent interfaces are assummed
    to be implemented in a base class of the current class.

    :keyword adapting: If set to ``True`` (not the default), fields
        that implement :class:`.IObject` will use an :class:`AdaptingFieldProperty`.
    """

    __my_names = set(__schema.names())
    __all_names = set(__schema.names(all=True))

    __not_my_names = __all_names - __my_names
    __not_my_names.update(omit)

    # The existing implementation relies on getframe(1) to find the caller,
    # which is us. So we do the same and copy to the real caller
    __frame = None
    __before = None
    __before = list(locals().keys())
    createFieldProperties(__schema, omit=__not_my_names)

    __frame = sys._getframe(1)
    for k, v in locals().items():
        if k not in __before:
            if adapting and sch_interfaces.IObject.providedBy(__schema[k]):
                v = AdaptingFieldProperty(__schema[k])
            __frame.f_locals[k] = v
