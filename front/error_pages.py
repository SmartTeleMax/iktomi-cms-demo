# -*- coding: utf-8 -*-
import os
import logging
import models
from iktomi.cli.base import Cli
from webob.exc import Request
from iktomi.web.reverse import Reverse
from iktomi.utils.storage import VersionedStorage
from front.urls.filters import Lang

logger = logging.getLogger(__name__)

class ErrorPages(Cli):
    'Development application'
    format = '%(levelname)s [%(name)s] %(message)s'

    def __init__(self, langs=('ru', 'en'), 
                 errors=('404', '429', '500', '504')):
        self.langs = langs
        self.errors = errors

    def command_generate(self):
        from front.environment import FrontEnvironment, environment
        from front.urls import app
        env = VersionedStorage(FrontEnvironment,
                               Request.blank('/'),
                               Reverse.from_handler(app))
        for lang in self.langs:
            env.lang = Lang(env, lang)
            env.models = getattr(models.front, lang)
            for error in self.errors:
                handler = environment | (
                        lambda env, data: env.render_to_string('errors/' + error, {}))
                tmpl = handler(env, VersionedStorage()).encode('utf-8')
                out = os.path.join(env.cfg.STATIC, lang, error+'.html')

                if os.path.isfile(out):
                    with open(out, 'r') as f:
                        existing = f.read()
                        if existing == tmpl:
                            continue

                with open(out, 'w') as f:
                    f.write(tmpl)
                logger.info("Rendered %s/%s.html", lang, error)

