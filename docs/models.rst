.. models documentation

Models
------

Important to any ODM/ORM is a way to provide utility and validation for the
documents that your application is storing. The goals of micromongo's models
are to:

* focus utility & validation into one object
* make utility, validation, and persistence part of documents being fetched
  from the database
* decrease code repetition by allowing queries and save to use a single managed
  connection pool

Despite mongodb's schemaless nature, there is often still a need to maintain 
some type and value guarantees on certain fields or maintain field requirements
on certain documents.  For instance, an ``Image`` being persisted to a database
might contain all different kinds of ``EXIF`` keys and values, but an integer
filesize (in bytes), URI, filetype, etc. could be required of all such 
documents.

The Model Base
~~~~~~~~~~~~~~

All user defined models should inherit from ``micromongo.models.Model``, which
is also imported into the top level ``micromongo`` namespace:

.. autoclass:: micromongo.Model

.. automethod:: micromongo.models.Model.new
.. automethod:: micromongo.models.Model.find
.. automethod:: micromongo.models.Model.save
.. automethod:: micromongo.models.Model.validate

The following keys cannot be used without colliding with names that Models use
internally or externally.  You should avoid these names if possible in your
documents:

    ``new``, ``find``, ``save``, ``validate``, ``keys``, ``items``, 
    ``values``, ``iterkeys``, ``iteritems``, ``itervalues``, ``update``,
    ``clear``, ``pre_save``, ``post_save``, ``collection``, ``database``,
    ``spec``

Many of these are to maintain a dict-like interface.  You can use a micromongo
model in anything that accepts map-like objects, but they do not inherit from
``dict``, so be careful when passing into C-code that expects an explicit dict.

Spec Documents
~~~~~~~~~~~~~~

Spec documents are dictionaries defined on ``Model`` classes that are a mapping
of document keys to ``Field`` objects that describe arbitrary validation on
those fields as well as requirements for any document of the model's type.

.. autoclass:: micromongo.spec.Field

.. automethod:: micromongo.spec.Field.typecheck

The way this looks in a micromongo Model is::

    from pprint import pprint
    from micromongo import Model, Field

    class TestModel(Model): 
        collection = 'test.test'
        spec = {
            'docid': Field(type=int, default=0),
            'req': Field(required=True),
            'enum': Field(type=['foo', 'bar'], default='foo'),
            'baz': Field(type=float),
        }
    
    t = TestModel.new()
    # t.items() => [('req', None), ('docid', 0), ('enum', 'foo')]

As you can see, ``docid`` and ``enum`` were given their defaults.  ``req``
was given a default of ``None`` because it is required but no default was given.
``baz`` was not added to the document, but if it is, its value will have to be
an instance of ``float``, or else saving the document will fail during
validation.

Creating Custom Field Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can create your own custom ``Field`` types by subclassing from ``Field``.
Suppose your needs include some kind of distance from a known point which must
be 0 or more::

    class PositiveNumberField(Field):
        """A field that checks that values are positive numbers, and also
        coerces values set on the field to float if it isn't already a
        number."""
        def __init__(self, **kwargs):
            def _type(value):
                if isinstance(value, (int, long, float)) and value >= 0:
                    return True
                return False
            kwargs['type'] = _type
            super(PositiveIntegerField, self).__init__(**kwargs)
        
        def pre_validate(self, value):
            if isinstance(value, (int, long, float)):
                return value
            try:
                return float(value)
            except ValueError:
                return value

This field will still take ``required`` and ``default``, but now the 
typecheck is embedded within the field class itself.  It also overrides 
the ``pre_validate`` method to provide some type coercion:

.. automethod:: micromongo.spec.Field.pre_validate

Document-level Validation
~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes, validation has to take into consideration the values of more than
one field.  Suppose you have a User model where you want either a ``twitter_id``
or an ``email_address`` field to be present and not the empty string.  You
can do this by implementing a ``pre_save`` hook on your Model object::

    class User(Model):
        collection = 'auth.user'
        spec = {
            'username' : Field(required=True, default="", type=str),
            'password' : Field(required=True, default="", type=str),
            'twitter_id' : Field(required=True, default=""),
            'email_address': Field(required=True, default=""),
        }

        def pre_save(self):
            if not any((self.twitter_id, self.email_address)):
                raise ValueError("User objects require either a twitter_id or"
                                 "email_address.")

Validation failures in general raise ``ValidationError``, so if you are doing
validation in your ``pre_save`` hook, you will want to raise this on failures
too.

You can also use ``pre_save`` to cache or calculate certain fields based off of
others in the model.  A text document meant to be saved in markdown can have
a calculated field ``prerendered`` that is set in this hook.

Registration Access
~~~~~~~~~~~~~~~~~~~

Micromongo keeps track of all models that have been registered.  For
applications that might want to use this data, a function providing a mapping
of their database location to the model class is provided:

.. autofunction:: micromongo.models.registered_models

