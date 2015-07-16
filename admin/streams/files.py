# -*- coding: utf-8 -*-
from datetime import date
from jinja2 import Markup

from iktomi.cms.forms import ModelForm
from iktomi.cms.stream import FilterForm as BaseFilter, ListFields, \
        ListField
from admin.streams.common.stream import I18nPublishStream
from admin.streams.common.fields import Field, TitleField, \
        DateFromTo, StateSelectField, IdField, SortField
from admin.streams.common import i18n_class_factory, convs, widgets
from admin.streams.common.fields import AjaxFileField

permissions = {'events-editor': 'rwxcdp'}

title = u'Файлы'
list_fields = ListFields(
    ListField('date', u'Дата', width='15%',
              transform = lambda obj: (obj.strftime('%d.%m.%Y')) if obj else ''),
    ('title', u'Заголовок'),
)
limit = 20
live_search = True
Model = 'AttachedFile'


def validate_format(conv, value):
    formats = conv.field.form.get_field('file_format').conv.choices
    if not value.ext.lstrip('.') in dict(formats):
        err = u"Недопустимый формат файла" + \
                '<br/>'.join([x[1] for x in formats])
        raise convs.ValidationError(Markup(err))
    return value


@i18n_class_factory(ModelForm)
def ItemForm(models):

    fields = [
        #AutoDateTimeField('date_created'),
        Field('date',
              conv=convs.Date(),
              widget=widgets.Calendar,
              label=u'Дата публикации',
              get_initial=lambda: date.today()),

        TitleField('title'),
        AjaxFileField('file',
                      widget=widgets.AjaxFileInput(upload_url='/_tmp_file'),
                      conv=AjaxFileField.conv(validate_format),
                      label=u'Файл'),
        Field('file_format',
              conv=convs.EnumChoice(
                    choices=[
                        ('pdf', u'PDF (.pdf)'),
                        ('doc', u'Microsoft Word (.doc)'),
                        ('rtf', u'Rich Text Format (.rtf)'),
                        ('zip', u'Zip архив (.zip)'),
                    ]),
              widget=widgets.Select(),
              permissions='r',
              label=u'Формат'),
        Field('file_size',
              permissions='r',
              label=u'Размер файла'),
    ]


class FilterForm(BaseFilter):

    fields = [
        StateSelectField(),
        IdField(),
        Field('search', label=u'Поиск'),
        DateFromTo('date'),
        SortField('sort',
                  choices=(('id', 'id'),
                           ('title', 'title'),
                           ('date', 'date')),
                  initial='-date')
    ]

    def filter_by__search(self, query, field, value):
        return query.filter(self.model.title.contains(value))


Stream = I18nPublishStream

