#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""micromongo tests."""

from unittest import TestCase, main

class AccountingMetaclassTest(TestCase):
    def test_model_accounting(self):
        from micromongo.models import AccountingMeta, Model
        cmap = AccountingMeta.collection_map
        class BlogPost(Model):
            database = "blog"
            collection = "post"

        class StreamEntry(Model):
            collection = "stream.stream_entry"

        class AutoModel(Model):
            pass

        self.assertEquals(cmap['stream.stream_entry'], StreamEntry)
        self.assertEquals(cmap['blog.post'], BlogPost)
        self.assertEquals(cmap['test_accountingmeta.auto_model'], AutoModel)

if __name__ == '__main__':
    main()
