# -*- coding: utf-8 -*-

from iktomi.utils import cached_property, weakproxy
from babel.support import Format
from babel.dates import format_timedelta, TIMEDELTA_UNITS
from .dates import format_date, format_datetime, format_daterange
from . import dates
from jinja2 import Markup


class delegate_cached(property):

    def __init__(self, to, what):
        self._to = to
        self._what = what

    def __get__(self, inst, cls=None):
        if inst is None:
            return self
        result = getattr(getattr(inst, self._to), self._what)
        inst.__dict__[self._what] = result
        return result


class Lang(str):

    def __new__(cls, env, name):
        self = str.__new__(cls, name)
        self._env = weakproxy(env)
        self.format = Format(name)
        return self

    @cached_property
    def root(self):
        return getattr(self._env.root, self)

    @cached_property
    def url_for(self):
        return self.root.build_url

    @cached_property
    def others(self):
        return tuple(lang for lang in self._env.langs if lang!=self)

    @cached_property
    def _translations(self):
        return self._env.get_translations(self)

    def gettext(self, msgid):
        message = self._translations.gettext(unicode(msgid))
        if isinstance(msgid, Markup):
            message = Markup(message)
        return message

    def ngettext(self, msgid1, msgid2, n):
        message = self._translations.ngettext(unicode(msgid1),
                                              unicode(msgid2), n)
        if isinstance(msgid1, Markup):
            message = Markup(message)
        return message

    def date(self, date, format=None):
        return format_date(date, format, locale=self)

    def datetime(self, datetime, format=None):
        return format_datetime(datetime, format, locale=self)

    def daterange(self, start, end):
        return format_daterange(start, end, locale=self)

    @cached_property
    def date_formats(self):
        return {'DATE': dates.DATE_FORMATS[self],
                'DATETIME': dates.DATETIME_FORMATS[self],
                'MONTH': dates.MONTH_FORMATS[self]}

    def timedelta2(self, seconds, **kwargs):
        for (i, (nm, tm)) in enumerate(TIMEDELTA_UNITS):
            if tm < seconds:
                result = format_timedelta(seconds, threshold=1, locale=self, **kwargs)
                smaller_tm = seconds % tm
                not_last = i < len(TIMEDELTA_UNITS) - 1
                if not_last and smaller_tm > TIMEDELTA_UNITS[i+1][1]:
                    result += ' ' + self.format.timedelta(smaller_tm, threshold=1, **kwargs)
                return result
        return format_timedelta(seconds, locale=self, **kwargs)


# date and datetime are reimplemented to use project-specific default formats
for name in ['currency', 'decimal', 'number', 'percent', 'scientific',
             'time', 'timedelta']:
    setattr(Lang, name, delegate_cached('format', name)) 
