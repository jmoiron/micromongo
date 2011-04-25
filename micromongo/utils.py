#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""micromongo utilities"""

import re
from functools import wraps

def memoize(function):
    """Memoizing function.  Potentially not thread-safe, since it will return
    resuts across threads.  Make sure this is okay with callers."""
    _cache = {}
    @wraps(function)
    def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in _cache:
            _cache[key] = function(*args, **kwargs)
        return _cache[key]
    return wrapper

def uncamel(name):
    """Convert a CamelCase name to a lower_underscore one.  From:
        http://stackoverflow.com/questions/1175208/
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


class OpenStruct(object):
    """Ruby style openstruct.  Implemented by myself millions of times."""
    def __init__(self, *d, **dd):
        if d and not dd:
            self.__dict__.update(d[0])
        else:
            self.__dict__.update(dd)
    def __iter__(self):  return iter(self.__dict__)
    def __getattr__(self, attr): return self.__getitem__(attr)
    def __getitem__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]
        return object.__getattribute__(self, item)
    def __setitem__(self, item, value): self.__dict__[item] = value
    def __delitem__(self, item):
        if item in self.__dict__:
            del self.__dict__[item]
    # the rest of the dict interface
    def get(self, key, *args):
        return self.__dict__.get(key, *args)
    def keys(self):  return self.__dict__.keys()
    def iterkeys(self): return self.__dict__.iterkeys()
    def values(self): return self.__dict__.values()
    def itervalues(self): return self.__dict__.itervalues()
    def items(self): return self.__dict__.items()
    def iteritems(self): return self.__dict__.iteritems()
    def update(self, d): self.__dict__.update(d)
    def clear(self): self.__dict__.clear()

