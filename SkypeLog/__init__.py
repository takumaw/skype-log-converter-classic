# This Python file uses the following encoding: utf-8
"""
SkypeLog is a Skype Log utilities for Python.
"""
__docformat__ = 'restructuredtext en'

from .message import *
from .reader import *
from .converter import *
from .locales import *

import logging

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

h = NullHandler()
logging.getLogger(__name__).addHandler(h)
