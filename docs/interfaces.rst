=======================
 nti.schema.interfaces
=======================

.. automodule:: nti.schema.interfaces
    :members:
    :undoc-members:

.. exception:: InvalidValue(*args, field=None, value=None)

    Adds a field specifically to carry the value that is invalid.

    .. deprecated:: 1.4.0
        This is now just a convenience wrapper around
        :class:`zope.schema.interfaces.InvalidValue` that calls
        :meth:`.zope.schema.interfaces.ValidationError.with_field_and_value`
        before returning the exception. You should always catch
        :class:`zope.schema.interfaces.InvalidValue`.
