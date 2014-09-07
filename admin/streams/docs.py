# -*- coding: utf-8 -*-
from iktomi.cms.forms import ModelForm
from iktomi.cms.stream import FilterForm as BaseFilter, ListFields, \
        ListField
from iktomi.cms.stream_actions import GetAction
from iktomi.cms.edit_log import EditLogHandler
from iktomi import web
from admin.streams.common.stream import I18nPublishStream, PreviewHandler
from admin.streams.common.fields import Field, TitleField,\
        SplitDateTimeField, DateFromTo,\
        StateSelectField, IdField, SortField, FieldBlock, \
        FieldSet, FieldList, LinksField, EditorNoteField, \
        SearchField
from admin.streams.common import i18n_class_factory, convs, widgets
from admin.streams.docs_html import body_conv, body_wysihtml5
from models.admin import EditorNote, WithState
import jinja2

permissions = {'editor': 'rwxcdp'}

Model = 'Doc'
title = u'Материалы'
limit = 20


list_fields = ListFields(ListField('date', u'Дата и время публикации',
                                   transform=lambda x: x.strftime('%d.%m.%Y %H:%M')),
                         ('title', u'Заголовок'))


def MediaField(name, model, label, stream_name=None):
    stream_name = stream_name or ('multimedia.'+name)
    return Field(name,
              conv=convs.ListOf(convs.ModelChoice(model=model),
                                required=False),
              widget=widgets.PopupStreamSelect(stream_name=stream_name,
                                               allow_create=True,
                                               classname="small-images",
                                               sortable=True),
              label=label)


title_field = Field('title',
              conv=convs.Html(convs.length(0, 1000),
                              convs.NoUpper, convs.StripTrailingDot,
                              convs.NoLocaleMix,
                              required=True,
                              allowed_elements=['sup', 'sub'],
                              allowed_attributes=[]),
              widget=widgets.Textarea,
              label=u'Заголовок')
summary_field = Field('summary',
              conv=convs.SummaryHtml(),
              widget=widgets.WysiHtml5(classname="tiny"),
              label=u'Лид')

def media_block(models):
    fields = [
        MediaField('photos_edit', models.Photo, u'Фото',
                   stream_name="multimedia.photos"),
        MediaField('photo_sets_edit', models.PhotoSet, u'Фотоподборка',
                   stream_name="multimedia.photo_sets"),
        ]
    return FieldBlock(u'Медиа-элементы', fields=fields,
                      classname='collapsable',
                      open_with_data=True)



def links_block(models):
    return FieldBlock(u'Блоки ссылок', fields=[
        FieldList(
              'link_blocks_edit',
              field=FieldSet(None,
                  conv=convs.ModelDictConv(model=models.DocLinkBlock),
                  fields=[
                      Field('id', conv=convs.Int(),
                            widget=widgets.HiddenInput(render_type='hidden')),
                      TitleField('title', max_length=250,
                                 label=u'Заголовок блока ссылок',
                                 widget=widgets.TextInput,
                                 initial=u'Смотрите также'),
                      LinksField(models, 'links_edit', models.DocLink),
                  ]
              ),
              widget=FieldList.widget(render_type='full-width'),
              order=True),
    ],
    hint=jinja2.Markup(
         u'<strong>Сохраните документ</strong>, чтобы сделать '
         u'добавленные блоки ссылок доступными '
         u'в текстовом редакторе. '),
    open_with_data=True)



editor_notes_block = FieldBlock(u'Особые пометки', fields=[
        EditorNoteField('',
                        model=EditorNote,
                        widget=EditorNoteField.widget(render_type='full-width'),
                        # Label of block is enough
                        label=None),
    ])


@i18n_class_factory(ModelForm)
def ItemForm(models):
    update__date_created = update__editor_notes = ModelForm.update_pass

    fields = (

        #FieldBlock(u'Ядро', fields=[

            #SplitDateTimeField(
            #      'date',
            #      label=u'Дата и время публикации'),
            title_field,
            summary_field,
            #Field('body',
            #      conv=body_conv,
            #      widget=body_wysihtml5,
            #      label=u'Текст'),
        #]),

        #media_block(models),
        #links_block(models),

        #FieldBlock(u'Разделы', fields=[
        #    Field('sections',
        #          conv=convs.ListOf(
        #              convs.ModelChoice(model=models.Section)),
        #          widget=widgets.PopupFilteredSelect(),
        #          label=u'Разделы'),
        #],
        #open_with_data=True),

        #editor_notes_block,
    )


@i18n_class_factory(BaseFilter)
def FilterForm(models):

    fields = [
        StateSelectField(),
        IdField(),
        Field('sections',
              conv=convs.ModelChoice(model=models.Section),
              widget=widgets.PopupFilteredSelect(),
              label=u'Sections'
            ),
        DateFromTo('date'),
        SortField('sort',
                  choices=(('id', 'id'),
                           ('title', 'title'),
                           ('date', 'date')),
                  initial='-date'),
        SearchField('title',
                    label=u'Заголовок'),
    ]

    def filter_by__title(self, query, field, value):
        Doc = self.env.models.Doc
        cond = getattr(Doc, field.name).contains(value)
        return query.filter(cond)


class DocLinkBlockHandler(GetAction):

    for_item = False
    available = [WithState.PRIVATE, WithState.PUBLIC]

    @property
    def app(self):
        return web.cases(
            web.match('/doc-link-block/<int:id>', 'doc_link_block') | self.doc_link_item,
            web.match('/photo-block/<int:id>', 'photo_block') | self.photo_item,
            web.match('/photo-set-block/<int:id>', 'photo_set_block') | self.photo_set_item,
            )


    def doc_link_item(self, env, data):
        doclink_block = env.db.query(env.models.DocLinkBlock).get(data.id)
        return env.render_to_response('doclink', {
            'doclink_block': doclink_block})

    def photo_item(self, env, data):
        Photo = env.models.Photo
        photo = env.db.query(Photo)\
                      .filter(Photo.state.in_(self.available))\
                      .filter_by(id=data.id).first()
        return env.render_to_response('photolink', {
            'photo': photo})

    def photo_set_item(self, env, data):
        PhotoSet = env.models.PhotoSet
        photo_set = env.db.query(PhotoSet)\
                      .filter(PhotoSet.state.in_(self.available))\
                      .filter_by(id=data.id).first()
        return env.render_to_response('photosetlink', {
            'photo_set': photo_set})


class Stream(I18nPublishStream):

    actions = I18nPublishStream.actions + [
        DocLinkBlockHandler(),
        PreviewHandler(),
        EditLogHandler(),
    ]


