# -*- coding: utf-8 -*-
from datetime import date, datetime
from iktomi.utils import cached_property
from jinja2 import Markup


class Context(object):

    def __init__(self, env):
        self.env = env

    def get_absolute_path(self, path):
        if '://' in path:
            return path
        return self.env.request.host_url + path

    @cached_property
    def today(self):
        return date.today()

    @cached_property
    def now(self):
        return datetime.now()

    @property
    def current_url(self):
        return self.env.request.url

    def language_links(self):
        env = self.env
        data = env.data
        if not env.current_location:
            return {}

        endpoint = env.current_location.split('.', 1)[1]
        published_items = getattr(env, 'published_items', [])
        links = {}
        for lang in env.lang.others:
            if not lang in env.allowed_languages:
                continue
            for item in published_items:
                if not hasattr(item, '_item_version') or \
                        not item._item_version('front', lang):
                    break
            else:
                d = data.as_dict()
                #if 'page' in d:
                #    del d['page']
                url = lang.root.build_subreverse(endpoint, **d)
                links[lang] = url
        return links

    _public_mark = Markup(' data-not-public')

    def public_marker(self, item):
        if not getattr(item, 'public', True):
            return self._public_mark
        return ''

    @cached_property
    def sections(self):
        db, models = self.env.db, self.env.models
        return db.query(models.Section).all()

