# -*- coding: utf-8 -*-
from iktomi.cms.forms import ModelForm
from iktomi.cms.stream import FilterForm as BaseFilter, ListFields
from iktomi.cms.edit_log import EditLogHandler
from admin.streams.common.stream import I18nPublishStream, PublishSortAction
from admin.streams.common.fields import SlugField, TitleField, \
        StateSelectField, IdField
from admin.streams.common import i18n_class_factory

permissions = {'editor': 'rwxcdp'}

title = u'Разделы новостей'
list_fields = ListFields(('title', u'Название'),
                         ('slug', u'Слаг'))
Model = 'Section'


@i18n_class_factory(ModelForm)
def ItemForm(models):

    fields = [
        TitleField('title', max_length=250, unique=True,
                   label=u'Название'),
        SlugField('slug'),
        TitleField('short_title', max_length=50, unique=True,
                   label=u'Короткое название'),
    ]


class FilterForm(BaseFilter):


    fields = [
        StateSelectField(),
        IdField(),
    ]


class Stream(I18nPublishStream):

    actions = [PublishSortAction(),
               EditLogHandler()]

