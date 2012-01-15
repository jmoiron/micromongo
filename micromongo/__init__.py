#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""micromongo __init__.py"""

from models import *
from spec import Field

VERSION = (0, 1, 4)

__all__ = ['connect', 'clean_connection', 'Model', 'Field', 'VERSION']


