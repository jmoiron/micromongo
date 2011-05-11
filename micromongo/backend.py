#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The backend contains a set of minimal subclasses around pymongo to get
the desired "as_class" behavior we want without resorting to inspect
hackery (which was too slow) or inserting hooks at every unpacking step,
subclassing much of pymongo and in the process creating a heavy maintenance
burden.

Because the bson wrapping can happen in C code, we don't have a lot of access
to that, so we introduce the concept of a class router which is any function
that takes a collection's full name and returns a new object of the appropriate
class to be used as a cursor's "as_class"."""

import os
from pprint import pprint

import pymongo

from pymongo.connection import Connection as PymongoConnection
from pymongo.database import Database as PymongoDatabase
from pymongo.collection import Collection as PymongoCollection
from pymongo.cursor import Cursor as PymongoCursor
from pymongo.son_manipulator import SONManipulator

def default_class_router(collection_full_name):
    return dict()

def from_env():
    """Get host/port settings from the environment."""
    if 'MICROMONGO_URI' in os.environ:
        return (os.environ['MICROMONGO_URI'],)
    host = os.environ.get('MICROMONGO_HOST', 'localhost')
    port = int(os.environ.get('MICROMONGO_PORT', 27017))
    return (host, port)

# NOTE: There's a current feature request with py_mongo to make the as_class
# option only apply to the highest level documents and not to the subdocuments.
#
#    https://jira.mongodb.org/browse/PYTHON-175
#
# until this is implemented, micromongo will have to add incoming son
# manipulators to make sure that subdocuments do not have the document class,
# which will most likely slow down saving but not impact other stuff
require_manipulator = map(int, pymongo.version.split('.')) < (1, 11)

class ModelSONManipulator(SONManipulator):
    """Manipulator to coerce all of instances of our Model class to dicts within
    the SON going into mongodb."""
    def transform_incoming(self, son, collection):
        from models import Model
        def unmodel(value):
            if isinstance(value, Model):
                value = dict(value)
            elif isinstance(value, list):
                return [unmodel(x) for x in value]
            else:
                return value
            for k,v in value.items():
                if isinstance(v, (Model, list)):
                    value[k] = unmodel(v)
            return value
        for k,v in son.items():
            if isinstance(v, (Model, list)):
                son[k] = unmodel(v)
        return son

class Connection(PymongoConnection):
    def __init__(self, *args, **kwargs):
        self.class_router = kwargs.pop('class_router', default_class_router)
        super(Connection, self).__init__(*args, **kwargs)

    def __getattr__(self, name):
        db = Database(self, name)
        if require_manipulator:
            db.add_son_manipulator(ModelSONManipulator())
        return db

class Database(PymongoDatabase):
    def __getattr__(self, name):
        return Collection(self, name)

class Collection(PymongoCollection):
    def find(self, *args, **kwargs):
        return Cursor(self, *args, **kwargs)

class Cursor(PymongoCursor):
    def __init__(self, *args, **kwargs):
        super(Cursor, self).__init__(*args, **kwargs)
        collection = self.__collection
        connection = collection.database.connection
        self.as_class = connection.class_router(collection.full_name)
        self.__as_class = connection.class_router(collection.full_name)
        # cache the iteration so we can iterate over results from these
        # cursors more than once;  we only do this if it is not "tailable"
        self.__itercache = []
        self.__fullcache = False

    def order_by(self, *fields):
        """An alternate to ``sort`` which allows you to specify a list
        of fields and use a leading - (minus) to specify DESCENDING."""
        doc = []
        for field in fields:
            if field.startswith('-'):
                doc.append((field.strip('-'), pymongo.DESCENDING))
            else:
                doc.append((field, pymongo.ASCENDING))
        return self.sort(doc)

    def __iter__(self):
        if self.__fullcache and not self.__tailable:
            return iter(self.__itercache)
        return self

    def next(self):
        """A `next` that caches the returned results.  Together with the
        slightly different `__iter__`, these cursors can be iterated over
        more than once."""
        if self.__tailable:
            return PymongoCursor.next(self)
        try:
            ret = PymongoCursor.next(self)
        except StopIteration:
            self.__fullcache = True
            raise
        self.__itercache.append(ret)
        return ret
