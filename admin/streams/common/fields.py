# -*- coding: utf-8 -*-
import json
import jinja2
from iktomi.forms.form_json import Field
from iktomi.cms.forms.fields import *
from collections import OrderedDict

from ..common import convs, widgets


def CheckBoxField(name, label, initial=None):
    params = dict(conv=convs.Bool,
                  widget=widgets.CheckBox(),
                  label=label)
    if initial is not None:
        params['initial'] = initial
    return Field(name, **params)


def SlugField(name, max_length=50, validators=(), unique=True,
              required=True, widget=widgets.TextInput, label=u'Слаг'):
    if unique:
        validators += (convs.DBUnique(),)
    return Field(name,
                 conv=convs.Char(convs.length(0, max_length),
                                 *validators,
                                 **{'required': required}),
                 widget=widget(),
                 label=u'Слаг')


def TextareaField(name, label=u'', max_length=1000, required=False,
                  widget=widgets.Textarea, initial='', validators=(), cls=Field):
    conv = convs.Char(convs.length(0, max_length),
                      convs.NoUpper, convs.NoLocaleMix,
                      *validators,
                      **{'required': required})
    return cls(name,
               conv=conv,
               initial=initial,
               widget=widget(),
               label=label)


def TitleField(name, label=u'Заголовок', max_length=1000, required=True,
               widget=widgets.Textarea, initial='', validators=(), cls=Field,
               unique=False):
    if unique:
        validators += (convs.DBUnique(),)
    conv = convs.Char(convs.length(0, max_length),
                      convs.NoUpper, convs.StripTrailingDot, convs.NoLocaleMix,
                      *validators,
                      **{'required': required})
    return cls(name,
               conv=conv,
               initial=initial,
               widget=widget(),
               label=label)


class SearchField(Field):

    conv = convs.Char
    widget = widgets.TextInput()
    label = u'Поиск'

    def filter_query(self, query, field, value):
        cond = getattr(self.form.model, field.name).contains(value)
        return query.filter(cond)


def UrlField(name, label=u'URL', max_length=250, required=False,
             domain_is_required=True, classname='link_source direct',
             unique=False):
    conv_args = [convs.length(0, max_length)]
    if unique:
        conv_args.append(convs.DBUnique())
    conv_kwargs = dict(domain_is_required=domain_is_required,
                       required=required)
    conv = convs.UrlConv(*conv_args, **conv_kwargs)
    return Field(name,
                 conv=conv,
                 widget=widgets.TextInput(classname=classname),
                 label=label)


class LinksConv(convs.TabbedModelDictConv):
    # XXX using index is not good idea: we have to redefine values if we remove
    #     some choices from the middle of tabs list.
    #     We do not use garant and consultant links on english version and in 
    #     HighlighZone.
    indicator_fields = {}
    title_field = 'ref_title'

    def to_python(self, value):
        _kind = value['_kind']
        for field, kind in self.indicator_fields.items():
            if kind != _kind:
                value[field] = None
            elif not value[field]:
                raise convs.ValidationError(u'вы должны выбрать материал или '\
                                            u'указать URL для ссылки')

        if value.get('ref_url') and self.title_field:
            self.assert_(value[self.title_field],
                         u'вы должны указать текст ссылки')
        return convs.ModelDictConv.to_python(self, value)


def LinksField(models, name, model, label=u'Ссылки', hint=None):

    tabs = [
        (None, 'id', '_kind'),
        (u'Документ', 'ref_doc', 'ref_title'),
        (u'Ссылка', 'ref_url', 'ref_title'),
    ]

    tabs = [x for x in tabs if getattr(model, x[1], None) is not None]
    indicator_fields = OrderedDict((x[1], i)
                            for i, x in enumerate(tabs[1:])
                            if getattr(model, x[1], None) is not None)

    fieldset = TabbedFieldSet(
        None, conv=LinksConv(model=model,
                             indicator_fields=indicator_fields),
        fields=[
            Field('id', conv=convs.Int(),
                  widget=widgets.HiddenInput),
            Field('ref_doc',
                  conv=convs.ModelChoice(model=models.Doc),
                  widget=widgets.PopupStreamSelect(stream_name='docs'),
                  label=u"Материал"),
            UrlField('ref_url'),
            Field('_kind',
                  conv=convs.Int(),
                  initial=0,
                  widget=widgets.HiddenInput),
            Field('ref_title',
                  conv=convs.Char(convs.length(0, 500)),
                  widget=widgets.TextInput(),
                  label=u'Текст ссылки'),
        ],
        trigger_field='_kind',
        tabs=tabs)

    fieldset.fields = [x for x in fieldset.fields
                       if getattr(model, x.name, None) is not None]

    return FieldList(name, order=True, field=fieldset, label=label, hint=hint)


class TabbedFieldSet(FieldSet):
    # XXX should not work???

    """
    Usage:
        TabbedFieldSet('fieldset_name'
            tabs = [
                (None, 'commonfield1', 'hidden_field'),
                (u'tab1', 'foo', 'bar'),
                (u'tab2', 'spam', 'eggs')
                ],
                select_tab = lambda field, value: 1,
                trigger_field = 'hidden_field',
                use_field = True, # Save only selected tab
                fields=[.....]
        )

    trigger field will contain number of selected tab
    if it's conv is int. if it's enumchoice, corresponding
    value will be selected (by index)
    """

    trigger_field = None
    use_trigger = True

    widget = FieldSet.widget(template = 'widgets/tabbed_fieldset')

    def __init__(self, *args, **kwargs):
        assert 'tabs' in kwargs, '"tabs" is required argument for TabbedFieldSet'
        super(TabbedFieldSet, self).__init__(*args, **kwargs)
        self.common_fields = []
        self.tabbed_fields = []
        index = 0
        for tab in self.tabs:
            if tab[0] is None:
                self.common_fields = tab[1:]
            else:
                self.tabbed_fields.append(dict(tab=tab[0], fields=tab[1:], index=index))
                index += 1
        self.tabbed_fields_list = []
        for field in [field.name for field in self.fields]:
            for tab in self.tabbed_fields:
                if field in tab['fields'] and field not in self.tabbed_fields_list:
                    self.tabbed_fields_list.append(field)

    @staticmethod
    def select_tab(field, value):
        # overrided in most cases

        if field.trigger_field:
            trigger = field.get_field(field.trigger_field)
            try:
                return int(field.form.raw_data[trigger.input_name])
            except (ValueError, KeyError):
                if value[field.trigger_field] is not None:
                    return value[field.trigger_field]
                return 0

        else:
            tabs = field.tabbed_fields
            tabs_fields = sum([list(t['fields']) for t in tabs], [])
            for tab in tabs:
                for f in tab['fields']:
                    if tabs_fields.count(f) > 1:
                        continue
                    if value[f]:
                        return tab['index']
        return 0

    @property
    def json_config(self):
        conf = dict(tabbed_fields=[tab['fields'] for tab in self.tabbed_fields],
                    common_fields=self.common_fields,
                    tabbed_fields_list=self.tabbed_fields_list,
                    active_tab=self.active_tab)

        if self.trigger_field:
            field = self.get_field(self.trigger_field)
            conf['trigger_id'] = field.id

        return json.dumps(conf)

    @property
    def active_tab(self):
        return self.select_tab(self, self.python_data)

    def get_field(self, name):
        for field in self.fields:
            if field.name == name:
                return field
        raise KeyError, name

    def get_initial(self):
        result = {}
        for field in self.fields:
            result[field.name] = field.get_initial()
        return self.conv.to_python_default(result)

    def accept(self, roles=None):
        if 'w' not in self.perm_getter.get_perms(self):
            raise convs.SkipReadonly
        result = self.python_data

        active_fields = self.tabbed_fields[self.active_tab]['fields']
        active_fields += self.common_fields

        result = dict(self.python_data)
        for field in self.fields:
            if field.writable:
                if self.trigger_field and self.use_trigger:
                    if field.name in active_fields:
                        result.update(field.accept())
                    else:
                        # XXX field blocks will not work!
                        result[field.name] = None
                else:
                    result.update(field.accept())
            else:
                # readonly field
                field.set_raw_value(self.form.raw_data,
                                    field.from_python(result[field.name]))
        self.clean_value = self.conv.accept(result)
        return {self.name: self.clean_value}


def CommonFieldBlock(*args, **kwargs):
    hint = jinja2.Markup(
            u"<strong>Поля, общие для всех языков.</strong><br/> "
            u"Изменение и публикация этих "
            u"полей для одного языка<br/> обновит данные "
            u"для всех языков.")
    kwargs.setdefault('hint', hint)
    return FieldBlock(*args, **kwargs)


class LowResImageField(AjaxImageField):

    show_thumbnail = False
    crop = False
    conv = AjaxImageField.conv(autocrop=True)
    widget = AjaxImageField.widget(classname="no-upload")

    def accept(self):
        return AjaxImageField.accept(self)
