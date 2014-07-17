# -*- coding: utf-8 -*-

import os, warnings
from gettext import c2py
from babel import Locale
from babel.support import Translations
from babel.messages.pofile import read_po
from babel.messages.plurals import get_plural


class POTranslations(Translations):

    def __init__(self, fp, locale):
        if not isinstance(locale, Locale):
            locale = Locale.parse(locale)
        self.locale = locale
        super(POTranslations, self).__init__(fp)
        self.plural = c2py(get_plural(locale).plural_expr)

    def _parse(self, fp):
        catalog = read_po(fp, locale=self.locale)
        self._catalog = c = {}
        for message in catalog._messages.itervalues():
            if message.pluralizable:
                for idx, string in enumerate(message.string):
                    c[message.id[0], idx] = string
            else:
                c[message.id] = message.string

    def ngettext(self, *args):
        return Translations.ngettext(self, *args)


def get_translations(dirname, locale, categories='messages'):
    if isinstance(categories, basestring):
        categories = [categories]
    translations = POTranslations(None, locale)
    for category in categories:
        fn = os.path.join(dirname, str(locale), category+'.po')
        if os.path.isfile(fn):
            with open(fn, 'U') as fp:
                t = POTranslations(fp, locale)
            translations.add(t)
        else:
            warnings.warn("File {} doesn't exist".format(fn))
    return translations
