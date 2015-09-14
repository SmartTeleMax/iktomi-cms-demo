# -*- coding: utf8 -*-
from webob.exc import HTTPNotFound, HTTPMovedPermanently
from iktomi.cms.auth.views import auth_required
from iktomi import web
from iktomi.web.filters import static_files, method
from iktomi.web.shortcuts import Rule
from iktomi.cms.flashmessages import flash_message_handler
from iktomi.cms.ajax_file_upload import FileUploadHandler
from admin.front_environment import front_environment
from admin.environment import environment, auth, static, file_manager
from front.urls import app_cases

from . import cfg, streams, views as h


front_app = web.cases(web.namespace('en'), web.namespace('ru')) | app_cases

load_tmp_file = FileUploadHandler(file_manager) # XXX both views are identical?
load_tmp_image = FileUploadHandler(file_manager)


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

        h.item_lock_view.app,
        h.tray_view.app,

        method('POST') | web.cases(
            web.match('/_tmp_img', 'load_tmp_file') | load_tmp_file,
            web.match('/_tmp_img', 'load_tmp_image') | load_tmp_image,
            Rule('/_post_note', h.post_note),
        ),

        streams.streams.to_app(),

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
