# -*- coding: utf-8 -*-

import re

_HAS_CYRILLIC_LETTER = re.compile(u'[а-яё]', re.U|re.I).search

def has_cyrillic(text):
    text = unicode(text)  # Isure we are working with unicode
    return _HAS_CYRILLIC_LETTER(text)

def should_be_translated(lang, text, plural=False):
    if lang=='en':
        return has_cyrillic(text)
    elif lang=='ru':
        return plural or not has_cyrillic(text)
    else:
        # Source could be in Russian or English only
        return True

def template_filter(catalog, message):
    text = message.id
    if message.pluralizable:
        text = text[0]
    return should_be_translated(catalog.locale.language, text,
                                plural=message.pluralizable)
