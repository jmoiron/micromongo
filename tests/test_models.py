#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""micromongo tests."""

from unittest import TestCase, main
from micromongo.backend import from_env
from micromongo import *

from uuid import uuid4

uuid = lambda: uuid4().hex

class ModelTest(TestCase):
    def tearDown(self):
        from micromongo.models import AccountingMeta
        AccountingMeta.collection_map = {}
        c = connect(*from_env())
        # dropping the db makes tests time consuming
        c.test_db.drop_collection('test_collection')

    def test_basic_wrapping(self):
        """Test basic model wrapping."""
        c = connect(*from_env())
        col = c.test_db.test_collection
        uuids = [uuid(), uuid(), uuid()]
        col.save({'docid': 0, 'uuid': uuids[0]})
        col.save({'docid': 1, 'uuid': uuids[1]})
        col.save({'docid': 2, 'uuid': uuids[2]})

        d1 = col.find_one({'docid': 0})
        self.assertEqual(type(d1), dict)
        self.assertEqual(d1['uuid'], uuids[d1['docid']])

        class Foo(Model):
            collection = col.full_name

        # sanity check the correctness of these documents
        d1 = col.find_one({'docid': 0})
        self.assertEqual(type(d1), Foo)
        self.assertEqual(d1.docid, 0)
        for i in range(3):
            d = col.find_one({'docid': i})
            self.assertEqual(d.uuid, uuids[d.docid])

        d2 = col.find_one({'docid': 1})
        d2.uuid = uuid()
        d2.save()

        d3 = col.find_one({'docid': 1})
        self.assertEqual(d3.uuid, d2.uuid)
        self.assertTrue(d3.uuid != uuids[d3.docid])

    def test_son_manipulator(self):
        """Test the SONManipulator, only with compatible pymongo versions."""
        from micromongo.backend import require_manipulator
        if not require_manipulator:
            return
        c = connect(*from_env())
        col = c.test_db.test_collection
        col.save({'docid': 17, 'subdoc': {'test': 1}})

        class Foo(Model):
            collection = col.full_name

        # first, test that saving this mess works once we hvae the class
        col.save({'docid': 18, 'subdoc': {'test': 1}})

        d = col.find_one({'docid': 18})
        d.subdoc.test = 3
        d.save()

        d2 = col.find_one({'docid': 18})
        self.assertEqual(d2.subdoc.test, 3)

class SONManipulatorTest(TestCase):
    def tearDown(self):
        from micromongo.models import AccountingMeta
        AccountingMeta.collection_map = {}
        c = connect(*from_env())
        # dropping the db makes tests time consuming
        c.test_db.drop_collection('test_collection')

    def test_dicts(self):
        """Test that nested dicts get un-documented."""
        # NOTE, the saves here would raise an exception and fail the test
        # if the underlying manipulator was not functioning properly
        c = connect(*from_env())
        col = c.test_db.test_collection

        class Foo(Model):
            collection = col.full_name

        col.save({'foo': {'bar': {'baz': 1}}})
        col.save({'foo': 1, 'bar': {'baz': 1}})

        self.assertEqual(Foo.find().count(), 2)

        for f in Foo.find():
            f.save()

    def test_lists(self):
        """Test that nested lists get un-documented."""
        # NOTE, the saves here would raise an exception and fail the test
        # if the underlying manipulator was not functioning properly
        c = connect(*from_env())
        col = c.test_db.test_collection

        class Foo(Model):
            collection = col.full_name

        col.save({'foo': [{'one': 1}, 'two', {'three': {'3':4}}]})
        col.save({'foo': [{'one': [1, 2, {'three': 3, 'four': [1,2,3, {
            'five': [5]}]}]}]})

        self.assertEqual(Foo.find().count(), 2)

        for f in Foo.find():
            f.save()

    def test_reiteration(self):
        """Test that cursors can be re-iterated."""
        c = connect(*from_env())
        col = c.test_db.test_collection

        class Foo(Model):
            collection = col.full_name

        col.save({'foo': [{'one': 1}, 'two', {'three': {'3':4}}]})
        col.save({'foo': [{'one': [1, 2, {'three': 3, 'four': [1,2,3, {
            'five': [5]}]}]}]})

        foos = Foo.find()

        self.assertEqual(len(list(foos)), 2)
        self.assertEqual(len(list(foos)), 2)

class MiscTest(TestCase):
    def test_version(self):
        """Test micromongo.VERSION."""
        import setup
        import micromongo
        self.assertTrue(bool(micromongo.VERSION))
        # make sure that it's the same as the version in setup.py
        self.assertEqual('.'.join(map(str, micromongo.VERSION)), setup.version)

