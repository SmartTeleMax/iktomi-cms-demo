# -*- coding: utf-8 -*-
#import inspect

import json
from jinja2 import Markup
from sqlalchemy.orm import sessionmaker
from functools import partial
from models.admin import AdminUser, DraftForm, EditLog
from iktomi.templates import Template, BoundTemplate as BaseBoundTemplate
from iktomi.templates.jinja2 import TemplateEngine
from iktomi.cms.auth.views import AdminAuth
from iktomi import web
from iktomi.web.filters import static_files
from iktomi.db import sqla
from iktomi.unstable.db.files import FileManager
from iktomi.unstable.db.sqla.files import filesessionmaker
from iktomi.utils.storage import storage_cached_property, storage_method, storage_property
from iktomi.utils import cached_property, quote_js
from iktomi.cms.item_lock import ItemLock
from i18n.translation import get_translations
from context import Context
from webob.exc import HTTPSeeOther

import models
from . import cfg
from .streams import streams
from .loners import loners
from .views import packer


static = static_files(cfg.STATIC, cfg.STATIC_URL)
file_manager = FileManager(cfg.FORM_TEMP, cfg.MEDIA_DIR,
                           cfg.FORM_TEMP_URL, cfg.MEDIA_URL)

def _get_db_maker(DATABASES):
    return filesessionmaker(
        sessionmaker(
            binds=sqla.multidb_binds(DATABASES,
                                     package=models,
                                     engine_params=cfg.DATABASE_PARAMS),
            autoflush=False,
        ),
        file_manager,
    )

db_maker = _get_db_maker(cfg.DATABASES)
memcache_client = cfg.CACHE
jinja_loader = TemplateEngine(cfg.TEMPLATES)
template_loader = Template(engines={'html': jinja_loader},
                           *cfg.TEMPLATES)
auth = AdminAuth(AdminUser, storage=memcache_client)


class AdminEnvironment(web.AppEnvironment):
    auth_model = AdminUser
    draft_form_model = DraftForm
    edit_log_model = EditLog
    cfg = cfg
    cache = memcache_client
    file_manager = file_manager
    login = None
    streams = streams
    loners = loners
    models = models
    lang = 'ru'

    @cached_property
    def url_for(self):
        return self.root.build_url

    @cached_property
    def url_for_static(self):
        return static.construct_reverse()

    @storage_cached_property
    def template(storage):
        return BoundTemplate(storage, template_loader)

    @storage_property
    def render_to_string(storage):
        return storage.template.render
    @storage_property
    def render_to_response(storage):
        return storage.template.render_to_response

    @storage_method
    def redirect_to(storage, name, qs, **kwargs):
        url = storage.url_for(name, **kwargs)
        if qs:
            url = url.qs_set(qs)
        return HTTPSeeOther(location=str(url))

    def get_translations(self, lang):
        return get_translations(cfg.I18N_TRANSLATIONS_DIR, lang,
                                ['iktomi-forms'])

    @cached_property
    def _translations(self):
        return self.get_translations(self.lang)

    @storage_method
    def gettext(self, msgid):
        message = self._translations.gettext(unicode(msgid))
        if isinstance(msgid, Markup):
            message = Markup(message)
        return message

    @storage_method
    def ngettext(self, msgid1, msgid2, n):
        message = self._translations.ngettext(unicode(msgid1),
                                              unicode(msgid2), n)
        if isinstance(msgid1, Markup):
            message = Markup(message)
        return message

    def json(self, data):
        return web.Response(json.dumps(data), content_type="application/json")

    @cached_property
    def db(self):
        return db_maker()

    @storage_cached_property
    def item_lock(storage):
        return ItemLock(storage)

    @storage_method
    def get_edit_url(storage, x):
        return streams.get_edit_url(storage, x)

@web.request_filter
def environment(env, data, next_handler):

    try:
        return next_handler(env, data)
    finally:
        env.db.close()


class BoundTemplate(BaseBoundTemplate):

    constant_template_vars = {
        'quote_js': quote_js,
    }

    def get_template_vars(self):
        d = dict(
            self.constant_template_vars,
            env = self.env,
            user = getattr(self.env, 'user', None),
            url_for = self.env.url_for,
            url_for_static = self.env.url_for_static,
            packed_js_tag=partial(packer.js_tag, self.env),
            packed_css_tag=partial(packer.css_tag, self.env),
            context = Context(self.env),
        )
        for key in self.env.cfg.TEMPLATE_IMPORT_SETTINGS:
            d[key] = getattr(self.env.cfg, key)
        return d

    def render(self, template_name, __data=None, **kw):
        r = BaseBoundTemplate.render(self, template_name, __data, **kw)
        return Markup(r)




