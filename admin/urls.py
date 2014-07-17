# -*- coding: utf8 -*-
from webob.exc import HTTPNotFound, HTTPMovedPermanently
from iktomi.cms.views import auth_required
from iktomi import web
from iktomi.web.filters import static_files, method
from .environment import environment, auth, static
from iktomi.web.shortcuts import Rule
from iktomi.cms.flashmessages import flash_message_handler
from admin.front_environment import front_environment
from front.urls import app_cases

from . import cfg, streams, loners, views as h


front_app = web.cases(web.namespace('en'), web.namespace('ru')) | app_cases


dynamic_app = \
      environment | \
      flash_message_handler | \
      web.cases(

    Rule('/pack.js', h.packer.js_packer),
    Rule('/pack.css', h.packer.css_packer),

    auth.login(),
    auth.logout(),

    auth | auth_required |
    web.cases(
        Rule('/', h.index, method='GET'),
        method('POST') | web.cases(
            Rule('/_update_lock/<string:item_id>/<string:edit_session>',
                 h.update_lock),
            Rule('/_force_lock/<string:item_id>',
                 h.force_lock),
            Rule('/_release_lock/<string:item_id>/<string:edit_session>',
                 h.release_lock),

            web.match('/_tmp_img', 'load_tmp_image') | h.load_tmp_image,
            Rule('/_post_note', h.post_note),
        ),
        web.prefix('/tray') | web.cases(
            Rule('/<int:tray>', h.tray_view.tray),
            web.prefix('/_') | web.method('POST', strict=True) | web.cases(
                Rule('/put', h.tray_view.put_to_tray),
                Rule('/user/put', h.tray_view.put_to_user_tray),
                Rule('/delete', h.tray_view.delete_from_tray),
            )
        ),
        streams.streams.to_app(),
        loners.loners.to_app(),
        web.prefix('/_front/<any(admin,front):version>/<any(en,ru):lang>', name='front') | 
            front_environment | front_app,

    ),

    HTTPNotFound, # XXX does not work without this
)

if getattr(cfg, 'SERVE_STATIC', False):
    app = web.cases(
        static,
        static_files(cfg.FORM_TEMP, cfg.FORM_TEMP_URL),
        static_files(cfg.MEDIA_DIR, cfg.MEDIA_URL),
        static_files(cfg.CMS_STATIC, cfg.CMS_STATIC_URL),
        static_files(cfg.FRONT_STATIC, cfg.FRONT_STATIC_URL),
        web.match('/favicon.ico', 'favicon') | HTTPMovedPermanently(location='/static/favicon.ico'),

        dynamic_app,
        HTTPNotFound, # XXX does not work without this
    )
else:
    app = web.cases(
        dynamic_app,
        HTTPNotFound, # XXX does not work without this
    )

if getattr(cfg, 'DEBUG', False):
    from iktomi import toolbar
    from iktomi.debug import debug
    app = toolbar.handler(cfg) | debug | app
