# -*- coding: utf-8 --
from iktomi.cms.forms import ModelForm
from iktomi.cms.edit_log import EditLogHandler
from admin.streams.common.stream import I18nPublishStream,\
        PreviewHandler, FilterForm as BaseFilter, ListFields
from iktomi.cms.ajax_file_upload import StreamImageUploadHandler
from admin.streams.common.fields import Field, StateSelectField, \
        IdField, SortField, TitleField, AjaxImageField, FieldList, \
        FieldSet
from admin.streams.common import i18n_class_factory, convs, widgets


Model = 'Gallery'

permissions = {'editor': 'rwxcdp'}

title = u'Галерея'
limit = 50

list_fields = ListFields(('title', u'Название'),)


@i18n_class_factory(ModelForm)
def ItemForm(models):

    fields = [
        TitleField('title', max_length=100,label=u'Название'),
        FieldList('images',
            order=False,
            field=FieldSet('pic',
                conv=convs.ModelDictConv(model=models.GalleryImage),
                fields=[
                  TitleField('title', max_length=100, label=u"Заголовок" ),
                  AjaxImageField('image',
                                 show_thumbnail=False,
                                 upload_url="/image_upload",
                                 widget=AjaxImageField.widget(allow_upload=True),
                                 label=u"Исходное изображение"),
                ],
                label=u'Изображениe',
            ),
            label=u"Изображения",
        )
    ]


class Stream(I18nPublishStream):

    actions = I18nPublishStream.actions + [
        PreviewHandler(),
        StreamImageUploadHandler(),
        ]
