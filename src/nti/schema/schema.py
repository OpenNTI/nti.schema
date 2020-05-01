#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Helpers for writing code that implements schemas.

This module contains code based on code originally from dm.zope.schema.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from zope.deferredimport import deprecatedFrom

from zope.interface.interfaces import IInterface
from zope.interface.interfaces import ISpecification
from zope.interface import providedBy
from zope.interface import implementer

from zope.schema._bootstrapinterfaces import IValidatable

from .interfaces import ISchemaConfigured

__docformat__ = "restructuredtext en"


def schemaitems(spec, _field_key=lambda x: x[1].order):
    """
    schemaitems(spec) -> [(name, field)]

    The schema part (fields) of interface specification *spec* as
    a list of (name, field) pairs, in their definition order.
    """
    sd = schemadict(spec)
    return sorted(sd.items(), key=_field_key)

def schemadict(spec):
    """
    The schema part (fields) of interface specification *spec* as map
    from name to field.

    *spec* can be:

    - A single Interface;
    - An object implementing ``zope.interfaces.interfaces.ISpecification``,
      such as that returned by ``providedBy(instance)`` or ``implementedBy(factory)``
      (an Interface is a special case of this).
    - A list, tuple, or iterable of Interfaces.
    """
    # ``zope.schema.getFields`` and ``getFieldsInOrder`` deal with a single
    # interface, only. So in the past, we handled the latter two cases
    # (which are the most common cases) by constructing a new interface
    # at runtime using the *spec* as its bases. But that's *really* slow, especially
    # if the hierarchy is complex. We can do a lot better if we pay attention to what
    # we're given.

    # First, boil it down to a list of Interface objects, in resolution order.
    if IInterface.providedBy(spec):
        iro = (spec,)
    elif ISpecification.providedBy(spec):
        iro = spec.__iro__
    else:
        iro = spec

    # Next, get the most derived fields.
    # ``zope.schema.getFields(iface)`` iterates across the interface,
    # which is the same as calling ``iface.names(all=True)`` (which
    # returns everything up the hierarchy). It then indexes into the
    # object to get the attribute. We can save some steps at the cost
    # of explicit method calls (as opposed to slots)
    result = {}
    is_field = IValidatable.providedBy
    for iface in iro:
        result.update(
            (name, attr)
            for name, attr
            in iface.namesAndDescriptions()
            if name not in result and is_field(attr)
        )
    return result



_marker = object()


@implementer(ISchemaConfigured)
class SchemaConfigured(object):
    """Mixin class to provide configuration by the provided schema components."""

    def __init__(self, **kw):
        schema = schemadict(self.sc_schema_spec())
        for k, v in kw.items():
            # might want to control this check
            if k not in schema:
                raise TypeError('non schema keyword argument: %s' % k)
            setattr(self, k, v)
        # provide default values for schema fields not set
        for f, fields in schema.items():
            if getattr(self, f, _marker) is _marker:
                # The point of this is to avoid hiding exceptions (which the builtin
                # hasattr() does on Python 2)
                setattr(self, f, fields.default)

    # provide control over which interfaces define the data schema
    SC_SCHEMAS = None

    def sc_schema_spec(self):
        """the schema specification which determines the data schema.

        This is determined by `SC_SCHEMAS` and defaults to `providedBy(self)`.
        """
        spec = self.SC_SCHEMAS
        return spec or providedBy(self)

class PermissiveSchemaConfigured(SchemaConfigured):
    """
    A mixin subclass of :class:`SchemaConfigured` that allows
    for extra keywords (those not defined in the schema) to silently be ignored.
    This is an aid to evolution of code and can be helpful in testing.

    To allow for one-by-one conversions and updates, this class defines an attribute
    ``SC_PERMISSIVE``, defaulting to True, that controls this behaviour.
    """

    SC_PERMISSIVE = True

    def __init__(self, **kwargs):
        if not self.SC_PERMISSIVE:
            super(PermissiveSchemaConfigured, self).__init__(**kwargs)
        else:
            _schema = schemadict(self.sc_schema_spec())
            kwargs = {k: kwargs[k] for k in kwargs if k in _schema}
            super(PermissiveSchemaConfigured, self).__init__(**kwargs)


deprecatedFrom("Moved to nti.schema.eqhash",
               "nti.schema.eqhash",
               'EqHash',
               '_superhash')
