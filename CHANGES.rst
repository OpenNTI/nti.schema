

=========
 Changes
=========


1.1.1 (unreleased)
==================

- Nothing changed yet.


1.1.0 (2016-07-29)
==================
- Add support for Python 3. *Note* the countries vocabulary will not
  be complete on Python 3.
- Drop the ``dolmen.builtins`` dependency.
- Drop the ``dm.zope.schema`` dependency.
- The ``plone.i18n`` dependency is Python 2 only (and can even be
  removed).
- The matchers in ``nti.schema.testing`` have been moved to
  ``nti.testing.matchers``.
- Using ``AdaptingFieldProperty`` will now raise the more specific
  ``SchemaNotProvided`` error instead of a ``TypeError`` if adapting
  the value fails.
- ``EqHash`` has moved from ``nti.schema.schema`` to
  ``nti.schema.eqhash``. A compatibility shim remains.
