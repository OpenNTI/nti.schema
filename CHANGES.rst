=========
 Changes
=========

1.14.0 (2020-03-27)
===================

- Require zope.interface 5.0.0 and related dependencies.

- Ensure all objects have consistent interface resolution orders.

- Add support for Python 3.8.


1.13.1 (2019-06-11)
===================

- ``StrippedValidTextLine`` should accept single character lines.

1.13.0 (2019-05-22)
===================

- Ensure ``StrippedValidTextLine`` correctly recognizes single character values
  as stripped. Previously, 'b' would have been rejected.

1.12.0 (2018-10-10)
===================

- JSON schemas report the schema for ``IObject`` fields
  and the schemas for the possible fields in ``IVariant``.

- Fields in JSON schemas may specify a JSON-serializable dictionary
  to be passed as the ``application_info`` schema value. See `issue 44
  <https://github.com/NextThought/nti.schema/issues/44>`_.

- JSON schemas now output more constraints automatically. See `issue
  47 <https://github.com/NextThought/nti.schema/pull/48>`_.

1.11.0 (2018-10-10)
===================

- JSON schemas now include nested ``value_type`` and ``key_type`` for
  collection and mapping fields. See `issue 42
  <https://github.com/NextThought/nti.schema/issues/42>`_.

- JSON schemas now include (translated) ``title`` and ``description``
  values for fields. See `issue 41
  <https://github.com/NextThought/nti.schema/issues/41>`_.


1.10.0 (2018-10-04)
===================

- Add ``nti.schema.fieldproperty.field_name`` to compensate for the
  mangling that ``FieldPropertyStoredThroughField`` does.


1.9.2 (2018-10-04)
==================

- Fix ``Variant`` and other implementations of ``IFromObject`` to stop
  passing known non-text values to ``fromUnicode`` methods. This only
  worked with certain fields (such as ``zope.schema.Number``) that
  could accept non-text values, usually by implementation accident,
  and could have surprising consequences. Instead, non-text values
  will be passed to the ``validate`` method.

- Fix ``Variant`` to stop double-validating values. The underlying
  ``fromUnicode``, ``fromBytes`` or ``fromObject`` methods were
  supposed to already validate.

1.9.1 (2018-10-03)
==================

- Make ``VariantValidationError`` and ``Variant`` have more useful
  string representations.

- Make ``fromObject`` methods more gracefully handle an AttributeError
  raised by an underlying ``fromUnicode`` method on non-string input
  (such as None). This is especially helpful for ``Variant`` fields
  because they can catch the error and continue to the next field.

- Fix ``Variant``, ``TupleFromObject``, ``DictFromObject``,
  ``ListFromObject`` and ``ListOrTupleFromObject`` to allow the
  ``missing_value`` (which defaults to ``None``) in their
  ``fromObject`` methods; passing that value in simply returns it
  without raising an exception if the field is not required. If the
  field is required, a ``RequiredMissing`` is raised. Previously the
  sequences raised a ``WrongType`` error, while ``Variant`` *may* or
  *may not* have raised an error, depending on the underlying fields
  in use.


1.9.0 (2018-10-02)
==================

- ``Variant`` objects now automatically add ``fromObject`` support to
  ``ICollection`` and ``IMapping`` fields that do not already provide
  it, if their ``value_type`` (and ``key_type``) qualify by being
  either an ``Object`` field, or something that provides
  ``IFromObject`` or can be made to, such as a collection or mapping.


1.8.0 (2018-09-28)
==================

- Add ``VariantValidationError``, an error raised by variant fields
  when none of their constituent fields could adapt or validate the
  value.


1.7.0 (2018-09-19)
==================

- Add support for ``IFromBytes`` in zope.schema 4.8.0.

- The ``Variant`` and ``ListOrTupleFromObject``, ``TupleFromObject``,
  ``DictFromObject`` fields all have tweaked behaviour in
  ``fromObject``. If the incoming value is a bytestring or text
  string, the underlying field's ``fromBytes`` and ``fromUnicode``
  will be called in preference to a ``fromObject``, if that method is
  implemented.

- ``ValidSet`` and ``UniqueIterable`` now implement ``fromObject``.

- All fields that implement ``fromObject`` now accept an ``Object``
  field for their ``value_type`` (and ``key_type`` in the case of
  ``DictFromObject``) and will attempt to adapt objects that do not
  provide the schema in ``fromObject``.

1.6.0 (2018-09-18)
==================

- Adjust the deprecated ``zope.schema.interfaces.InvalidValue`` to be
  a simple alias for ``zope.schema.interfaces.InvalidValue`` (while
  preserving the constructor) for improved backwards compatibility.


1.5.0 (2018-09-11)
==================

- Add support for zope.schema 4.7.0; drop support for older versions.


1.4.2 (2018-09-10)
==================

- Fix the ``repr`` of ``nti.schema.interfaces.InvalidValue``. See
  `issue 26 <https://github.com/NextThought/nti.schema/issues/26>`_.

- ``nti.schema.jsonschema`` turns more abstract field types into
  concrete types. See `issue 29 <https://github.com/NextThought/nti.schema/issues/29>`_.

1.4.1 (2018-09-10)
==================

- Make ``nti.schema.interfaces.InvalidValue`` a class again. It is
  deprecated. See `issue 24 <https://github.com/NextThought/nti.schema/issues/24>`_.


1.4.0 (2018-09-10)
==================

- Drop support for ``dm.zope.schema`` fields, in particular the
  ``Object`` field. The validation performed by ``zope.schema.Object``
  is much improved.

- Drop support for ``zope.schema`` older than 4.6.1.

- Deprecate ``nti.schema.field.Number``.

- Add support for Python 3.7.

1.3.3 (2018-09-07)
==================

- Minor fix for changes in zope.schema 4.6.0 (import
  ``BeforeObjectAssignedEvent`` from its new, but still private, location).


1.3.2 (2017-10-24)
==================

- Depend on zope.deferredimport >= 4.2.1 to be able to generate Sphinx
  documentation.
- Clean up code to match PEP8.


1.3.1 (2017-10-18)
==================

- Fix an ``UnboundLocalError`` on Python 3 in the ``Variant`` field.
  See `issue 14 <https://github.com/NextThought/nti.schema/issues/14>`_.


1.3.0 (2017-07-06)
==================

- Drop the Python 2 dependency on ``plone.i18n`` in favor of the new
  library ``nti.i18n``, which supports Python 3. If ``plone.i18n`` is
  installed, it *should not* be configured (ZCML), but its utility
  objects can be looked up by either interface.


1.2.0 (2017-05-17)
==================

- Remove use of ``unicode_literals``.

- Add support for Python 3.6.

- The ``SchemaConfigured`` constructor doesn't hide errors when
  checking for properties on Python 2. See `issue 11
  <https://github.com/NextThought/nti.schema/issues/11>`_.


1.1.3 (2017-01-17)
==================

- Add info to minLength validation message.


1.1.2 (2016-09-14)
==================

- Add ``Acquisition`` and ``zope.event`` as install dependencies.
  Previously they were only pulled in via the ``test`` extra.


1.1.1 (2016-09-08)
==================

- Substantial speedups to the hash functions generated by ``EqHash``.
- Substantial speedups to the equality functions generated by ``EqHash``.

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
