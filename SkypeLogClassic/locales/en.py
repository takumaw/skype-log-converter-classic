# This Python file uses the following encoding: utf-8
"""Locale: English
"""

class LocaleDict:
    def get_text(self, text, formatdict=None):
        if formatdict:
            translated_text = text % formatdict
        else:
            translated_text = text
        return translated_text
