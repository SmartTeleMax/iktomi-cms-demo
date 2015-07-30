# -*- coding: utf-8 --
from iktomi.cms.forms import ModelForm
from iktomi.cms.edit_log import EditLogHandler
from admin.streams.common.stream import I18nPublishStream,\
        PreviewHandler, FilterForm as BaseFilter, ListFields
from admin.streams.common.fields import Field, StateSelectField, \
        IdField, SortField, TitleField, FieldList, FieldSet
from admin.streams.common import i18n_class_factory, convs, widgets


Model = 'Term'

permissions = {'editor': 'rwxcdp'}

title = u'Глоссарий'
limit = 50

list_fields = ListFields(('title', u'Термин'),
                         )


@i18n_class_factory(ModelForm)
def ItemForm(models):

    fields = [
        TitleField('title', max_length=100, unique=True, label=u'Термин'),
        Field('summary',
              conv=convs.Html(required=True,
                              allowed_elements=convs.Html.allowed_elements
                                     -set(['ul', 'ol', 'li', 'blockquote'])),
              widget=widgets.WysiHtml5(classname="tiny"),
              label=u'Краткое описание'),
        Field('body',
              conv=convs.Html(),
              widget=widgets.WysiHtml5(),
              label=u'Текст'),
    ]
    
    if models.db == 'admin':
        fields.append(
                FieldList('synonyms',
                          order=False,
                          field=Field('title',
                                      initial='test',
                                      conv=convs.Char(convs.length(0, 10000),
                                                      required=True),
                                      widget=widgets.TextInput(classname='big')),
                          label=u'Синонимы и аббревиатуры (для автоопределения)'),
        )


class FilterForm(BaseFilter):

    fields = [
        StateSelectField(),
        IdField(),
        SortField('sort',
                  choices=(('id', 'id'),
                           ('title', 'title')),
                  initial='title')
    ]



class Stream(I18nPublishStream):

    actions = I18nPublishStream.actions + [
        PreviewHandler(),
        EditLogHandler(),
        ]
