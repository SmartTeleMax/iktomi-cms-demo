# -*- coding: utf-8 -*-
from iktomi.cms.forms import ModelForm
from iktomi.cms.stream import FilterForm as BaseFilter, ListFields
from iktomi.cms.edit_log import EditLogHandler
from admin.streams.common.stream import I18nPublishStream
from admin.streams.common.fields import SearchField,\
        StateSelectField, IdField, SortField, TitleField
from admin.streams.common import i18n_class_factory

permissions = {'editor': 'rwxcdp'}

Model = 'PhotoSource'
title = u"Источники изображений"

list_fields = ListFields(('title', u'Название'))
live_search = True
#wheel_all = {'wheel': 'rw'}


@i18n_class_factory(ModelForm)
def ItemForm(models):

    fields = [
        TitleField('title', max_length=250, unique=True,
                   label=u'Название'),
    ]


class FilterForm(BaseFilter):

    fields = [
        StateSelectField(),
        IdField(),
        SearchField('title',
                    label=u'Название'),
        SortField('sort',
                  choices=(('id', 'id'),
                           ('title', 'title'),
                           ),
                  initial='id')
    ]

    def filter_by__title(self, query, field, value):
        query = query.filter(self.model.title.like('%' + value + '%'))
        return query


class Stream(I18nPublishStream):

    actions = [
        EditLogHandler(),
    ]
