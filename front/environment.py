# -*- coding: utf-8 -*-
import json
import jinja2
from jinja2 import Markup
from datetime import datetime
from iktomi.templates import Template, BoundTemplate as BaseBoundTemplate
from iktomi.templates.jinja2 import TemplateEngine
from iktomi import web
from iktomi.db import sqla
from iktomi.unstable.db.files import ReadonlyFileManager
from iktomi.unstable.db.sqla.files import filesessionmaker
from iktomi.web.filters import static_files
from iktomi.utils.storage import storage_method, storage_cached_property
from iktomi.unstable.db.sqla.public_query import PublicQuery
from iktomi.utils import cached_property
from front.context import Context
from webob.exc import HTTPSeeOther
#from front.urls.for_object import url_for_object
from i18n.translation import get_translations
import models.front

import cfg

static = static_files(cfg.STATIC, cfg.STATIC_URL)
static_reverse = static.construct_reverse()
_static_hashes = {}


class BoundTemplate(BaseBoundTemplate):

    constant_template_vars = dict(
            [(key, getattr(cfg, key))
             for key in cfg.TEMPLATE_IMPORT_SETTINGS])

    def get_template_vars(self):
        lang = self.env.lang
        d = dict(
            lang = lang,
            url = lang.root,
            url_for = lang.url_for,
            #url_for_object = self.env.url_for_object,
            url_for_static = self.env.url_for_static,
            gettext = lang.gettext,
            ngettext = lang.ngettext,
            now = datetime.now(),
        )
        return d


class FrontTemplateEngine(TemplateEngine):

    def _make_env(self, paths):
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(paths),
            autoescape=True,
            extensions=[
                'jinja2.ext.i18n',
                'jinja2.ext.loopcontrols',
                'jinja2.ext.with_',
            ],
        )
        env.extend(cfg=cfg)
        # Null translations in globals are replaced (actually masked with
        # locals) returned by BoundTemplate.get_template_vars().
        env.install_null_translations()
        env.globals = dict(env.globals,
                           **BoundTemplate.constant_template_vars)
        return env


_file_manager = ReadonlyFileManager(cfg.MEDIA_DIR, cfg.MEDIA_URL)
db_maker = filesessionmaker(sqla.session_maker(cfg.DATABASES,
                                               engine_params=cfg.DATABASE_PARAMS,
                                               query_cls=PublicQuery),
                            _file_manager)
memcache_client = cfg.CACHE
jinja_loader = FrontTemplateEngine(cfg.TEMPLATES)
template_loader = Template(engines={'html': jinja_loader},
                           *cfg.TEMPLATES)


class FrontEnvironment(web.AppEnvironment):
    cfg = cfg
    cache = memcache_client
    models = models.front

    def __init__(self, *args, **kwargs):
        super(FrontEnvironment, self).__init__(*args, **kwargs)
        self.allowed_languages = ['en', 'ru']

        # Used to build interlanguage links.
        # A list of objects that must have version on target language to
        # indicate that same url exists on that version.
        # Should be immutable.
        self.published_items = ()

        self.template_data = dict(
            # env object is self._root_storage, self is just StorageFrame
            context = Context(self._root_storage))

    @storage_method
    def url_for_static(self, path):
        return self.cfg.STATIC_URL + path

    @cached_property
    def url_for(self):
        return self.root.build_url

    @storage_cached_property
    def template(storage):
        return BoundTemplate(storage, template_loader)

    def get_translations(self, lang):
        return get_translations(cfg.I18N_TRANSLATIONS_DIR, lang,
                                ['front', 'iktomi-forms'])

    @storage_method
    def render_to_string(storage, template_name, _data, *args, **kwargs):
        _data = dict(storage.template_data, **_data)
        result = storage.template.render(template_name, _data, *args, **kwargs)
        return Markup(result)

    @storage_method
    def render_to_response(self, template_name, _data,
                           content_type="text/html"):
        _data = dict(self.template_data, **_data)
        return self.template.render_to_response(template_name, _data,
                                                content_type=content_type)

    @storage_method
    def redirect_to(storage, name, qs, **kwargs):
        url = storage.url_for(name, **kwargs)
        if qs:
            url = url.qs_set(qs)
        return HTTPSeeOther(location=str(url))

    def json(self, data):
        return web.Response(json.dumps(data), content_type="application/json")

    @cached_property
    def db(self):
        return db_maker()


@web.request_filter
def environment(env, data, next_handler):
    env.data = data # XXX hack!
    try:
        return next_handler(env, data)
    finally:
        env.db.close()

