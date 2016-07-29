#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test support for schemas and interfaces, mostly in the form of Hamcrest matchers.

.. $Id$
"""

from __future__ import print_function, absolute_import, division

from zope.deferredimport import deprecatedFrom

deprecatedFrom("Matchers live in nti.testing.matchers",
               "nti.testing.matchers",
               "provides", "implements",
               "verifiably_provides", "validly_provides",
               "validated_by", "not_validated_by")
