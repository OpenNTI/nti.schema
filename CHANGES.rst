

Changes
=======


1.1.0 (unreleased)
------------------

- The matchers in ``nti.schema.testing`` have been moved to
  ``nti.testing.matchers``.
- Using ``AdaptingFieldProperty`` will now raise the more specific
  ``SchemaNotProvided`` error instead of a ``TypeError`` if adapting
  the value fails.
