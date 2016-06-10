# This Python file uses the following encoding: utf-8
"""
SkypeLog is a Skype Log utilities for Python.
"""
__docformat__ = 'restructuredtext en'

from . import message
from . import reader
from . import converter
from . import locales

import logging

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

h = NullHandler()
logging.getLogger(__name__).addHandler(h)
