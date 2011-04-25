#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""micromongo models"""

from uuid import uuid4
from pprint import pprint

from pymongo import Connection as PymongoConnection

from micromongo.utils import OpenStruct, uncamel
from micromongo.backend import Connection

required = uuid4().hex

__connection_args = tuple()
__connection = None

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

    def save(self):
        if hasattr(self, 'pre_save'):
            pre_save(self)
        database, collection = self._collection_key.split('.')
        self.verify()
        __connection[database][collection].save(self)
        if hasattr(self, 'post_save'):
            post_save(self)


