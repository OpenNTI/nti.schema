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

from zope.schema.interfaces import IValidatable
from zope.schema.fieldproperty import FieldProperty

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
    schemadict(spec) -> dict

    The schema part (fields) of interface specification *spec* as map
    from name to field.

    The return value *must* be treated as immutable.

    *spec* can be:

    - A single Interface;
    - An object implementing ``zope.interfaces.interfaces.ISpecification``,
      such as that returned by ``providedBy(instance)`` or ``implementedBy(factory)``
      (an Interface is a special case of this).
    - A list, tuple, or iterable of Interfaces.

    In the first two cases, the results will be cached using the
    usual interface caching rules. That means that changes to interface bases,
    or changes to what an object or class provides or implements, will be properly
    detected. However, if you simply assign a new field to an existing interface,
    it may not be detected (things like ``Interface.get()`` also fail in that case)
    unless you call ``Interface.changed()``.

    .. versionchanged:: 1.15.0
       Added caching and re-implemented the schemadict algorithm for speed.
       The return value must now be treated as immutable.
    """
    try:
        cache_in = spec._v_attrs # pylint:disable=protected-access
    except AttributeError:
        # As of zope.interface 5.0, these are always there, so
        # this must be just an iterable.
        pass
    else:
        try:
            return cache_in['__nti_schema_schemadict']
        except TypeError:
            assert cache_in is None
            cache_in = spec._v_attrs = {}
        except KeyError:
            pass

    # ``zope.schema.getFields`` and ``getFieldsInOrder`` deal with a
    # single interface, only. So in the past, we handled the latter
    # two cases (which are the most common cases, especially the
    # ``providedBy`` case) by constructing a new interface at runtime
    # using the *spec* as its bases. But that's *really* slow,
    # especially if the hierarchy is complex. We can do a lot better
    # if we pay attention to what we're given.

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

    # If we have somewhere to stick a cache, do so.
    # Note that we don't look up _v_attrs again, just in case it changed
    # concurrently.
    try:
        cache_in['__nti_schema_schemadict'] = result
    except NameError:
        pass

    return result



_marker = object()


@implementer(ISchemaConfigured)
class SchemaConfigured(object):
    """
    Mixin class to provide configuration by the provided schema
    components.

    This class is fastest if most of the attributes are represented
    by ``FieldProperty`` objects.

    .. versionchanged:: 1.15
       Special case ``FieldProperty`` instances found in the type
       when checking whether a value has been provided. We now assume
       that if there is no matching item in the dict with the same name,
       no value was provided. Note that if the schema field contained in the
       ``FieldProperty`` did something funky in its ``bind()`` method to
       this object, that will no longer happen at construction time.
       This can be turned of by setting ``SC_OPTIMIZE_FIELD_PROPERTY`` to false.

       If you add a FieldProperty to a ``SchemaConfigured`` class after an instance
       has been created, you must call ``sc_changed``.
    """

    SC_OPTIMIZE_FIELD_PROPERTY = True

    def __init__(self, **kw):
        schema = schemadict(self.sc_schema_spec())
        for k, v in kw.items():
            # might want to control this check
            if k not in schema:
                raise TypeError('non schema keyword argument: %s' % k)
            setattr(self, k, v)

        # provide default values for schema fields not set.
        # In bench_schemaconfigured.py, if the fields are FieldProperty objects found in the
        # type, checking for whether they are set or not took 96% of the total time.
        # We can be much faster (33us -> 9.1us) if we special case this, without hurting
        # the non-FieldProperty case too much.
        if self.SC_OPTIMIZE_FIELD_PROPERTY:
            schema = self.__elide_fieldproperty(schema)

        for field_name, schema_field in schema.items():
            if field_name in kw:
                continue
            # TODO: I think we could do better by first checking
            # to see if field_name is in vars(type(self))?
            if getattr(self, field_name, _marker) is _marker:
                # The point of this is to avoid hiding exceptions (which the builtin
                # hasattr() does on Python 2)
                setattr(self, field_name, schema_field.default)

    __FP_KEY = '__SchemaConfigured_elide_fieldproperty'

    @classmethod
    def __elide_fieldproperty(cls, schema):
        try:
            matches = cls.__dict__[cls.__FP_KEY]
        except KeyError:
            matches = cls.__find_FieldProperty_that_match_schema(schema)
            setattr(cls, cls.__FP_KEY, matches)

        return {k: v for k, v in schema.items() if k not in matches}


    @classmethod
    def __find_FieldProperty_that_match_schema(cls, schema_dict):
        result = set()
        for field_name, schema_field in schema_dict.items():
            try:
                # If these are descriptors, this runs code. We don't look in the
                # type's __dict__ because we would need to manually walk up the mro().
                kind_value = getattr(cls, field_name)
            except AttributeError:
                continue

            # pylint:disable=protected-access
            if isinstance(kind_value, FieldProperty) \
               and kind_value._FieldProperty__field == schema_field:
                # These are data-descriptors, with both __get__ and
                # __set__, so they're in full control. They automatically return
                # the default value of the field (that they have), so we don't
                # need to copy it down from our schema field.
                result.add(field_name)
        return result


    @classmethod
    def sc_changed(cls, orig_changed=None):
        """
        Call this method if you assign a fieldproperty to this class after creation.
        """
        if cls.__FP_KEY in cls.__dict__:
            # If this happens concurrently and we hit a super class, that's
            # fine.
            try:
                delattr(cls, cls.__FP_KEY)
            except AttributeError: # pragma: no cover
                pass

    # provide control over which interfaces define the data schema
    SC_SCHEMAS = None

    def sc_schema_spec(self):
        """the schema specification which determines the data schema.

        This is determined by `SC_SCHEMAS` and defaults to `providedBy(self)`.
        """
        return self.SC_SCHEMAS or providedBy(self)

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
