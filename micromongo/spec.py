#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""micromongo spec documents & validation"""

from functools import partial
from uuid import uuid4

__all__ = ['validate', 'make_default', 'Field']

no_default = uuid4().hex

class Field(object):
    """A base Field type, which itself can be used pretty reasonably to get
    type coersion, field defaults, etc.  If ``required`` is True, then
    validation will fail if this field is NOT present in the document.
    ``default`` is the default value to give this field in a new document;
    if it is None and the field is not required, the field is not added to
    new documents.  ``type`` is an object that can perform validation on
    this field;  see documentation for ``Field.typecheck``."""
    def __init__(self, required=False, default=None, type=None):
        self.required = required
        self._default = default
        self._typecheck = self.typecheck(type)

    def typecheck(self, t):
        """Create a typecheck from some value ``t``.  This behaves differently
        depending on what ``t`` is.  It should take a value and return True if
        the typecheck passes, or False otherwise.  Override ``pre_validate``
        in a child class to do type coercion.

        * If ``t`` is a type, like basestring, int, float, *or* a tuple of base
          types, then a simple isinstance typecheck is returned.

        * If ``t`` is a list or tuple of instances, such as a tuple or list of
          integers or of strings, it's treated as the definition of an enum
          and a simple "in" check is returned.

        * If ``t`` is callable, ``t`` is assumed to be a valid typecheck.

        * If ``t`` is None, a typecheck that always passes is returned.

        If none of these conditions are met, a TypeError is raised.
        """
        if t is None:
            return lambda x: True

        def _isinstance(types, value):
            return isinstance(value, types)

        def _enum(values, value):
            return value in values

        if t.__class__ is type:
            return partial(_isinstance, t)
        elif isinstance(t, (tuple, list)):
            if all([x.__class__ is type for x in t]):
                return partial(_isinstance, t)
            return partial(_enum, t)
        elif callable(t):
            return t
        raise TypeError('%r is not a valid field type' % r)

    def _get_default(self):
        if self.required:
            return self._default
        if self._default is not None:
            return self._default
        return no_default
    default = property(_get_default)


    def pre_validate(self, value):
        """A hook called before a value is validated.  Implement this to
        do type coercion;  say, to create an IntegerField that attempts to
        turn values into integers, or other more complex manipulations."""
        return value

    def validate(self, value):
        """Validate a value for this field.  If the field is invalid, this
        will raise a ValueError.  Runs ``pre_validate`` hook prior to
        validation, and returns value if validation passes."""
        value = self.pre_validate(value)
        if not self._typecheck(value):
            raise ValueError('%r failed type check' % value)
        return value

def make_default(spec):
    """Create an empty document that follows spec.  Any field with a default
    will take that value, required or not.  Required fields with no default
    will get a value of None.  If your default value does not match your
    type or otherwise customized Field class, this can create a spec that
    fails validation."""
    doc = {}
    for key, field in spec.iteritems():
        if field.default is not no_default:
            doc[key] = field.default
    return doc

def validate(document, spec):
    """Validate that a document meets a specification.  Returns True if
    validation was successful, but otherwise raises a ValueError."""
    if not spec:
        return True
    missing = []
    for key, field in spec.iteritems():
        if field.required and key not in document:
            missing.append(key)

    failed = []
    for key, field in spec.iteritems():
        if key in document:
            try: document[key] = field.validate(document[key])
            except ValueError: failed.append(key)

    if missing or failed:
        if missing and not failed:
            raise ValueError("Required fields missing: %s" % (missing))
        if failed and not missing:
            raise ValueError("Keys did not match spec: %s" % (failed))
        raise ValueError("Missing fields: %s, Invalid fields: %s" % (missing, failed))
    # just a token of my kindness, a return for you
    return True

