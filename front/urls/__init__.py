# -*- coding: utf-8 -*-
from webob.exc import HTTPNotFound, HTTPMovedPermanently
from iktomi import web
from iktomi.web.filters import static_files
from front import cfg

from front.environment import environment, static
from .filters import Rule, domain, lang_domains, cache

from front import views

__all__ = ['app']

dynamic_app = cache() | web.cases(
    Rule('/', views.index),
    web.prefix('/events', name="events") | views.events.events.app,
)


if getattr(cfg, 'SERVE_STATIC', False):
    app_cases = web.cases(
      dynamic_app,

      static,
      static_files(cfg.MEDIA_DIR, cfg.MEDIA_URL),
      web.match('/favicon.ico', 'favicon') | HTTPMovedPermanently('/static/favicon.ico'),

      HTTPNotFound,
    )
else:
    app_cases = web.cases(
      dynamic_app,
      # XXX Without this it polutes log with "Application returned None instead
      # of Response object" messages
      HTTPNotFound,
    )


app = environment | domain() | lang_domains('ru', 'en') | app_cases

if getattr(cfg, 'DEBUG', False):
    from iktomi import toolbar
    from iktomi.debug import debug
    app = toolbar.handler(cfg) | debug | app
