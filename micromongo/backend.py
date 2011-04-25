#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A set of minimal subclasses around pymongo to get the desired "as_class"
behavior we want without resorting to inspect hackery (which was too slow).

Because the bson wrapping can happen in C code, we don't have a lot of access
to that, so we introduce the concept of a class router which is any function
that takes a collection's full name and returns a new object of the appropriate
class to be used as a cursor's "as_class"."""

from pymongo.connection import Connection as PymongoConnection
from pymongo.database import Database as PymongoDatabase
from pymongo.collection import Collection as PymongoCollection
from pymongo.cursor import Cursor as PymongoCursor

def default_class_router(collection_full_name):
    return dict()

class Connection(PymongoConnection):
    def __init__(self, *args, **kwargs):
        self.class_router = kwargs.pop('class_router', default_class_router)
        super(Connection, self).__init__(*args, **kwargs)

    def __getattr__(self, name):
        return Database(self, name)

class Database(PymongoDatabase):
    def __getattr__(self, name):
        return Collection(self, name)

class Collection(PymongoCollection):
    def find(self, *args, **kwargs):
        return Cursor(self, *args, **kwargs)

class Cursor(PymongoCursor):
    def __init__(self, *args, **kwargs):
        collection = self.__collection
        connection = collection.database.connection
        kwargs['as_class'] = connection.class_router(collection.full_name)
        super(Cursor, self).__init__(*args, **kwargs)

