# -*- coding: utf-8 -*-
from iktomi.cms.stream import *
from iktomi.cms.publishing.stream import *
from iktomi.cms.publishing.i18n_stream import *

from functools import partial
from admin.front_environment import call_with_front_env
#from front.urls.for_object import url_for_object
from iktomi.cms.preview import PreviewHandler
from iktomi.cms.publishing.stream_sortables import PublishSortForm, PublishSortAction
from front import cfg as front_cfg


class PreviewHandler(PreviewHandler):

    @staticmethod
    def get_url(item, env, data):
        return url_for_object(env, item)

    def item_url(self, env, data, item):
        return call_with_front_env(env, data, partial(self.get_url, item))

    def external_url(self, env, data, item):
        if getattr(item, 'public', True):
            url = self.item_url(env, data, item).as_url
            index = call_with_front_env(env, data, 
                    lambda e, d: e.lang.root.index.as_url)
            domain = front_cfg.DOMAINS[0]
            return url.replace(index, 'http://{}/'.format(domain)
                                        if env.lang == 'ru' else 
                                      'http://{}.{}/'.format(env.lang, domain))


class PublishSortForm(PublishSortForm):

    ordering_field = 'order_position'


class PublishSortAction(PublishSortAction):

    @cached_property
    def ListItemForm(self):
        return getattr(self.stream.config, 'ListItemForm', PublishSortForm)


