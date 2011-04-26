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

