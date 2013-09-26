# This Python file uses the following encoding: utf-8

class Locale:
    def __init__(self):
        pass
    
    def set_locale(self, locale):
        self.localemod = __import__(locale, globals(), locals())
        self.localedict = self.localemod.LocaleDict()
        self.locale = locale

    def get_text(self, text, formatdict=None):
        return self.localedict.get_text(text, formatdict)