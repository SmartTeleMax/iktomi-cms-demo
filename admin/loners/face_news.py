# -*- coding: utf-8 -*-
from iktomi.forms import Field
from iktomi.cms.forms import ModelForm
from iktomi.cms.publishing.i18n_loner import I18nPublishLoner
from iktomi.cms.edit_log.views import EditLogHandler
from admin.streams.common import convs, widgets, i18n_class_factory
from admin.streams.common.stream import PreviewHandler
from admin.front_environment import call_with_front_env

Model = 'FaceNews'
title = u'Главные новости'

permissions = {'editor': 'rwp'}


@i18n_class_factory(ModelForm)
def ItemForm(models):

    fields = [
        Field('docs_edit',
              conv=convs.ListOf(
                  convs.ModelChoice(model=models.Doc,
                                    condition=models.Doc.public),
                  required=True),
              widget=widgets.PopupStreamSelect(
                unshift=True,
                stream_name="docs",
                default_filters={'state': models.Doc.PUBLIC}),
              label=u'Главные новости'),
    ]


class PreviewHandler_(PreviewHandler):

    def item_url(self, env, data, item):
        def get_url(env, data):
            return env.lang.root.index
        return call_with_front_env(env, data, get_url)


class Loner(I18nPublishLoner):
    actions = I18nPublishLoner.actions + [
        PreviewHandler_(),
        EditLogHandler(),
        ]
