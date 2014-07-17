# -*- coding: utf-8 -*-
from iktomi.cms.forms import ModelForm
from iktomi.cms.stream import FilterForm as BaseFilter, ListFields, \
        ListField
from iktomi.cms.edit_log import EditLogHandler
from admin.streams.common.stream import I18nPublishStream#, PreviewHandler
from admin.streams.common.fields import Field, TitleField, \
        SplitDateTimeField, DateFromTo, StateSelectField, IdField, SortField,\
        SearchField
from admin.streams.common import i18n_class_factory, convs, widgets

permissions = {'editor': 'rwxcdp'}
Model = 'PhotoSet'

def get_thumb_url(img):
    if img is not None and img.image_tiny is not None:
        return img.image_tiny
    return {'url':''}

title = u'Фотоподборки'
list_fields = ListFields(
    ('id', u'ID'),
    ListField('index_photo', u'', image=True, transform=get_thumb_url),
    ListField('date', u'Дата', transform=lambda dt: dt.strftime('%d.%m.%Y %H:%M')),
    ('title', u'Заголовок'),
)
limit = 20


@i18n_class_factory(ModelForm)
def ItemForm(models):
    fields = [
        TitleField('title'),
        SplitDateTimeField(
              'date',
              required=True,
              label=u'Дата и время'),
        Field('date_end',
              label=u'Дата окончания',
              conv=convs.Date(),
              widget=widgets.Calendar),

        Field('photos_edit',
              conv=convs.ListOf(
                  convs.ModelChoice(model=models.Photo),
                  required=True),
              widget=widgets.PopupStreamSelect(
                  stream_name='multimedia.photos',
                  template="widgets/popup_stream_select_photos",
                  allow_create=True),
              label=u'Фотографии'),

        Field('index_photo',
              conv=convs.ModelChoice(model=models.Photo, required=False),
              widget=widgets.HiddenInput,
              label=None
              ),
    ]

    presavehooks = [u'CheckPhotoOrder', u'CheckMainPhoto']


class FilterForm(BaseFilter):

    fields = [
        StateSelectField(),
        IdField(),
        DateFromTo('date'),
        SortField('sort',
                  choices=(('id', 'id'),
                           ('date', 'date')),
                  initial='-date'),
        SearchField('title',
                    label=u'Заголовок'),
    ]


class Stream(I18nPublishStream):

    actions = [
        #PreviewHandler(),
        EditLogHandler(),
        ]
