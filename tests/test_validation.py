#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test validation and other routines in micromongo.spec"""

from unittest import TestCase

from micromongo import *
from micromongo.backend import from_env
from micromongo.spec import *

class ValidationTest(TestCase):
    def tearDown(self):
        from micromongo.models import AccountingMeta
        AccountingMeta.collection_map = {}
        c = connect(*from_env())
        # dropping the db makes tests time consuming
        c.test_db.drop_collection('test_collection')

    def test_make_default(self):
        spec = {
            'docid': Field(type=int, default=0),
            'req': Field(required=True),
            'enum': Field(type=['foo', 'bar'], default='foo'),
            'baz': Field(type=float),
        }

        doc = make_default(spec)

        # should be: {
        #   'docid': 0,
        #   'req': None,
        #   'enum': 'foo',
        # }

        self.assertEqual(len(doc.keys()), 3)
        self.assertEqual(doc['docid'], 0)
        self.assertEqual(doc['req'], None)
        self.assertEqual(doc['enum'], 'foo')


    def test_validation(self):
        c = connect(*from_env())
        col = c.test_db.test_collection

        class Foo(Model):
            collection = col.full_name
            spec = {
                'docid': Field(type=int, default=0),
                'req': Field(required=True),
                'enum': Field(type=['foo', 'bar'], default='foo'),
                'baz': Field(type=float),
                'any' : Field(type=(int, float, long)),
            }

        # this should work
        f = Foo.new(baz=10.4)
        f.save()

        # f should also have _id set now..
        self.assertEqual(len(f.keys()), 5)
        self.assertEqual(f.docid, 0)
        self.assertEqual(f.req, None)
        self.assertAlmostEqual(f.baz, 10.4)

        f.baz = 10
        self.assertRaises(ValueError, f.save)

        f.baz = 1.0
        f.save()

        f.enum = 'baz'
        self.assertRaises(ValueError, f.save)

        f.enum = 'bar'
        f.save()

        del f['req']
        self.assertRaises(ValueError, f.save)

        f.req = "okay"
        f.save()

        f.docid = 1234L
        self.assertRaises(ValueError, f.save)

        f.docid = 0
        f.any = 1234
        f.save()
        f.any = 1234L
        f.save()
        f.any = 123.4
        f.save()

