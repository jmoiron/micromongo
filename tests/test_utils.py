#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""micromongo tests."""

from unittest import TestCase, main

class UncamelTest(TestCase):
    def test_uncamel(self):
        """Test the un-camel-casing routines in util."""
        from micromongo.utils import uncamel
        self.assertEquals(uncamel('CamelCase'), 'camel_case')
        self.assertEquals(uncamel('CamelCamelCase'), 'camel_camel_case')
        self.assertEquals(uncamel('already_un'), 'already_un')
        self.assertEquals(uncamel('Capitalized'), 'capitalized')
        self.assertEquals(uncamel('getHTTPResponseCode'), 'get_http_response_code')
