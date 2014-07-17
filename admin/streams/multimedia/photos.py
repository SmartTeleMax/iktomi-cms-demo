# -*- coding: utf-8 -*-
from datetime import date

from iktomi.cms.forms import ModelForm
from iktomi.cms.stream import FilterForm as BaseFilter, ListFields, \
        I18nLabel, ListField
from iktomi.cms.ajax_file_upload import StreamImageUploadHandler
from iktomi.cms.edit_log import EditLogHandler
from admin.streams.common.stream import I18nPublishStream
from admin.streams.common.fields import Field, FieldBlock, TitleField, \
        DateFromTo, StateSelectField, \
        IdField, SortField, CommonFieldBlock, SearchField
from admin.streams.common import i18n_class_factory, convs, widgets
from admin.streams.common.fields import AjaxImageField, LowResImageField

permissions = {'editor': 'rwxcdp'}

Model = 'Photo'
title = u'Фотобанк'
list_fields = ListFields(
    ListField('image_tiny', u'', image=True),
    ListField('date', u'Дата', transform=lambda dt: dt.strftime('%d.%m.%Y') if dt else ''),
    ('title', u'Подпись'),
)

limit = 20


class SourceField(Field):

    default = 1

    def get_initial(self):
        return self.conv.to_python(self.default)


@i18n_class_factory(ModelForm)
def ItemForm(models):

    fields = (

        CommonFieldBlock(u'', classname='', fields=[
            Field('date',
                  conv=convs.Date(),
                  widget=widgets.Calendar,
                  label=u'Дата публикации',
                  get_initial=date.today),
        ]),

        FieldBlock(I18nLabel(u'Переводимые поля', models.lang), fields=[
            TitleField('title', label=u'Подпись'),
        ], open_with_data=True),



        CommonFieldBlock(u'', fields=[
            SourceField(
                'source',
                conv=convs.ModelChoice(model=models.PhotoSource,
                                       required=True),
                widget=widgets.PopupStreamSelect(stream_name='multimedia.photo_sources',
                                                 allow_create=True),
                label=u'Источник'),

            AjaxImageField(
                'image',
                required=True,
                show_thumbnail=False,
                show_size=False,
                label = u'Фото в исходном разрешении'),
            AjaxImageField(
                'image_big',
                widget=AjaxImageField.widget(classname="no-upload"),
                label=u'Большой размер'),
            LowResImageField(
                'image_medium',
                label=u'Средний размер'),
            LowResImageField(
                'image_tiny',
                label=u'Маленький размер'),

            AjaxImageField(
                'image_small',
                widget=AjaxImageField.widget(classname="no-upload"),
                label=u'Квадратная обрезка'),
        ])
    )


class FilterForm(BaseFilter):

    fields = [
        StateSelectField(),
        IdField(),
        Field('search', label=u'Поиск'),
        DateFromTo('date', label=u'Дата публикации'),
        SortField('sort',
                  choices=(('id', 'id'),
                           ('date', 'date')),
                  initial='-date'),
        SearchField('title',
                    label=u'Заголовок'),
    ]


class Stream(I18nPublishStream):

    actions = [StreamImageUploadHandler(),
               EditLogHandler()]

