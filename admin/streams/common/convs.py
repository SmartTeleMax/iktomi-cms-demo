# -*- coding: utf-8 -*-
from iktomi.cms.forms.convs import *
from iktomi.forms.convs import __all__ as _all1
from chakert import Typograph
from iktomi.utils.html import Cleaner

import re
from iktomi.utils import cached_property
from models.common.fields import ExpandableMarkup


_all2 = locals().keys()


def NoUpper(field, value):
    if value and not (value.upper()!=value or value.lower() == value):
        raise ValidationError(u'Не нужно писать БОЛЬШИМИ БУКВАМИ')
    return value


def StripTrailingDot(field, value):
    if value:
        value = value.rstrip('.')
    return value

_EN, _RU, _TAIL = '[a-zA-Z]', u'[а-яА-ЯёЁ]', '\w*'
_locale_mix_re = re.compile('(RU+ENTAIL|EN+RUTAIL)'
                            .replace('EN', _EN)\
                            .replace('RU', _RU)\
                            .replace('TAIL', _TAIL), re.UNICODE)
_roman_re = re.compile(u'^[IVXLCDMХ]+$', re.UNICODE)
_en_re = re.compile(_EN)
_ru_re = re.compile(_RU)
_mix_replacements = [('A', u'А'),
                     ('a', u'а'),
                     ('C', u'С'),
                     ('c', u'с'),
                     ('o', u'о'),
                     ('O', u'О'),
                     ('e', u'е'),
                     ('E', u'Е'),
                     ('T', u'Т'),
                     ('K', u'К'),
                     ('M', u'М')]

def _fix_locale(value, replace_table={}):
    failures, replaced = [], []
    def _replace_mix(mix):
        s = mix.group()
        if replace_table.get(s):
            replaced.append(s)
            return replace_table[s]
        if _roman_re.match(s):
            replaced.append(s)
            return s.replace(u'Х', 'X')
        en = _en_re.findall(s)
        ru = _ru_re.findall(s)
        if len(ru) == 1 and len(en) > 1:
            repl = dict((v, k) for k,v in _mix_replacements)
            if ru[0] in repl:
                replaced.append(s)
                return s.replace(ru[0], repl[ru[0]])
        elif len(en) == 1 and len(ru) > 1:
            repl = dict(_mix_replacements)
            if en[0] in repl:
                replaced.append(s)
                return s.replace(en[0], repl[en[0]])

        failures.append(s)
        return s
    val = value
    if isinstance(val, ExpandableMarkup):
        val = val.markup
    val = _locale_mix_re.sub(_replace_mix, val)
    return type(value)(val), failures, replaced


def NoLocaleMix(conv, value):
    val, failures, _ = _fix_locale(value)
    if failures:
        raise ValidationError(u'Смесь раскладок клавиатуры в словах: ' +
                              u', '.join(failures))
    return val


class UrlConv(Char):

    domain_is_required = True
    domain_part = (
        r'https?://'
        r'(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}'
        r'(?::\d+)?')

    domain_required_regex = re.compile(
        r'^' + domain_part + r'(?:/\S*)?$', re.IGNORECASE)
    domain_optional_regex = re.compile(
        r'^(?:' + domain_part + r')?(?:/\S*)?$', re.IGNORECASE)
    error_regex=u"Неверный формат URL"

    @cached_property
    def regex(self):
        if self.domain_is_required:
            return self.domain_required_regex
        return self.domain_optional_regex


class TabbedModelDictConv(ModelDictConv):
    indicator_fields = {'ref_url': 1}
    default_kind = 0

    def to_python_default(self, value):
        return ModelDictConv.to_python(self, value)

    def from_python(self, value):
        if value is None:
            return dict([(f.name, f.get_initial())
                         for f in self.field.fields])
        for key, kind in self.indicator_fields.items():
            if getattr(value, key, None):
                value._kind = kind
                break
        else:
            value._kind = self.default_kind
        return super(TabbedModelDictConv, self).from_python(value)


class Digits(Char):

    _nondigit_sub = re.compile('[^0-9]+', re.U).sub

    def clean_value(self, value):
        value = Char.clean_value(self, value)
        return self._nondigit_sub('', value)


# =================== Html ==================

class TypoCleaner(Cleaner):

    typograph = True
    lang = None

    def extra_clean(self, doc):
        if self.typograph:
            Typograph.typograph_tree(doc, self.lang)

        Cleaner.extra_clean(self, doc)


class Html(Html):

    validators = (NoLocaleMix,)
    Cleaner = TypoCleaner

    @cached_property
    def lang(self):
        if getattr(self.env.models, 'lang', None):
            return self.env.models.lang
        parent = self.field
        while parent:
            if getattr(parent.label, 'lang'):
                return parent.label.lang
            parent = parent.parent
        raise AttributeError()

    @cached_property
    def cleaner(self):
        return self.Cleaner(lang=self.lang,
                            allow_tags=self.allowed_elements,
                            safe_attrs=self.allowed_attributes,
                            allow_classes=self.allowed_classes,
                            allowed_protocols=self.allowed_protocols,
                            drop_empty_tags=self.drop_empty_tags,
                            dom_callbacks=self.dom_callbacks,
                            )


class SummaryHtml(Html):

    allowed_elements = Html.allowed_elements - \
            set(['ul', 'ol', 'li', 'blockquote'])


class ExpandableHtml(Html):
    '''
        Converter for ExpandableHtml column type, used
        for markup which should be preprocessed on front-end.
    '''

    def to_python(self, value):
        value = Html.to_python(self, value)
        return ExpandableMarkup(value)

    def from_python(self, value):
        if isinstance(value, ExpandableMarkup):
            value = value.markup
        return Html.from_python(self, value)


# ==================== End Html ==========================


# Expose all variables defined after imports and all variables imported from
# parent module
__all__ = [x for x
           in set(locals().keys()) - (set(_all2) - set(_all1))
           if not x.startswith('_')]
del _all1, _all2
