#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Helpers for writing code that implements schemas.

.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from dm.zope.schema.schema import SchemaConfigured, schemadict, Object as ObjectBase
ObjectBase.check_declaration = True

class PermissiveSchemaConfigured(SchemaConfigured):
    """
    A mixin subclass of :class:`SchemaConfigured` that allows
    for extra keywords (those not defined in the schema) to silently be ignored.
    This is an aid to evolution of code and can be helpful in testing.

    To allow for one-by-one conversions and updates, this class defines an attribute
    ``SC_PERMISSIVE``, defaulting to True, that controls this behaviour.
    """

    SC_PERMISSIVE = True

    def __init__( self, **kwargs ):
        if not self.SC_PERMISSIVE:
            super(PermissiveSchemaConfigured,self).__init__( **kwargs )
        else:
            _schema = schemadict(self.sc_schema_spec())
            for k in kwargs.keys():
                if k not in _schema:
                    kwargs.pop( k )
            super(PermissiveSchemaConfigured,self).__init__( **kwargs )

from zope.deferredimport import deprecatedFrom

deprecatedFrom("Moved to nti.schema.eqhash",
               "nti.schema.eqhash",
               'EqHash',
               '_superhash')
