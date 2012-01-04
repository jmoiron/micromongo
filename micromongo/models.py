#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""micromongo models"""

from pprint import pprint, pformat

from pymongo import Connection as PymongoConnection

from micromongo.utils import OpenStruct, uncamel
from micromongo.backend import Connection
from micromongo.spec import validate, make_default

__all__ = ['current', 'connect', 'clean_connection', 'Model']

__connection_args = tuple()
__connection = None

def current():
    global __connection
    return __connection

def connect(*args, **kwargs):
    """Connect to the database.  Passes arguments along to
    ``pymongo.connection.Connection`` unmodified.

    The Connection returned by this proxy method will be used by micromongo
    for all of its queries.  Micromongo will alter the behavior of this
    conneciton object in some subtle ways;  if you want a clean one, call
    ``micromongo.clean_connection`` after connecting."""
    global __connection, __connection_args
    __connection_args = (args, dict(kwargs))
    # inject our class_router
    kwargs['class_router'] = class_router
    __connection = Connection(*args, **kwargs)
    return __connection

def clean_connection():
    """Get a clean Connection object on the database.  This connection will
    not have the behavioral changes that micromongo's regular connection
    will have."""
    global __connection_args, __connection
    if not __connection_args and __connection is None:
        raise Exception('must call `connect` before `clean_connection`')
    return PymongoConnection(*__connection_args[0], **__connection_args[1])

def registered_models():
    """Return the AccountingMeta's model mapping, which is a dictionary of
    keys in the form of "db.collection" to model classes."""
    return dict(AccountingMeta.collection_map)

def class_router(collection_full_name):
    return AccountingMeta.route(collection_full_name)

class AccountingMeta(type):
    """Metaclass for all model classes.

    This class keeps track of the database & collection that each model
    covers, and is used by the ``DocumentClassProxy`` to look up the right
    model class to wrap around objects."""
    collection_map = {}

    def __new__(cls, name, bases, attrs):
        cls = type.__new__(cls, name, bases, attrs)
        if '__classinit__' in attrs:
            cls.__classinit__ = staticmethod(cls.__classinit__.im_func)
        cls.__classinit__(cls, attrs)
        return cls

    @staticmethod
    def route(collection_full_name):
        return AccountingMeta.collection_map.get(collection_full_name, dict)


class Model(OpenStruct):
    """Micromongo Model object."""
    __metaclass__ = AccountingMeta

    def __classinit__(cls, attrs):
        if cls.__name__ == 'Model':
            return
        if 'collection' in attrs and 'database' in attrs:
            key = '%s.%s' % (attrs['database'], attrs['collection'])
        elif 'collection' in attrs:
            key = attrs['collection']
        else:
            module = cls.__module__.split('.')[-1]
            key = '%s.%s' % (uncamel(module), uncamel(cls.__name__))
        cls._collection_key = key
        AccountingMeta.collection_map[key] = cls

    @classmethod
    def new(cls, *args, **kwargs):
        """Create a new instance of this model based on its spec and either
        a map or the provided kwargs."""
        new = cls(make_default(getattr(cls, 'spec', {})))
        new.update(args[0] if args and not kwargs else kwargs)
        return new

    @classmethod
    def find(cls, *args, **kwargs):
        """Run a find on this model's collection.  The arguments to ``Model.find``
        are the same as to ``pymongo.Collection.find``."""
        database, collection = cls._collection_key.split('.')
        return current()[database][collection].find(*args, **kwargs)

    @classmethod
    def find_one(cls, *args, **kwargs):
        """Run a find_one on this model's collection.  The arguments to
        ``Model.find_one`` are the same as to ``pymongo.Collection.find_one``."""
        database, collection = cls._collection_key.split('.')
        return current()[database][collection].find_one(*args, **kwargs)

    def validate(self):
        """Validate this object based on its spec document."""
        return validate(self, getattr(self, 'spec', None))

    def save(self):
        """Save this object to the database.  Behaves very similarly to
        whatever collection.save(document) would, ie. does upserts on _id
        presence.  If methods ``pre_save`` or ``post_save`` are defined, those
        are called.  If there is a spec document, then the document is
        validated against it after the ``pre_save`` hook but before the save."""
        if hasattr(self, 'pre_save'):
            self.pre_save()
        database, collection = self._collection_key.split('.')
        self.validate()
        _id = current()[database][collection].save(dict(self))
        if _id: self._id = _id
        if hasattr(self, 'post_save'):
            self.post_save()

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, pformat(dict(self)))

