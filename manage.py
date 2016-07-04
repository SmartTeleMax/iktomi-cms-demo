#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
import os, sys, logging
from importlib import import_module
import cfg_common

import iktomi
from iktomi.cli import manage
from iktomi.cli.lazy import LazyCli

#from app import wsgi_app, db_maker

IKTOMI_DIR = os.path.dirname(os.path.normpath(iktomi.__file__))


@LazyCli
def db_command():
    import admin
    import front
    from admin.environment import _get_db_maker

    # XXX is it ok to just merge Databases configs?
    DATABASES = dict()
    DATABASES.update(front.cfg.DATABASES)
    DATABASES.update(admin.cfg.DATABASES)

    db_maker = _get_db_maker(DATABASES)

    from models import initial
    from iktomi.cli import sqla
    from models.generate import generators
    return sqla.Sqla(
        db_maker,
        metadata={name: import_module('models.'+name).metadata
                  for name in DATABASES},
        initial=initial.install,
        generators=generators,
    )


@LazyCli
def i18n_command():
    from i18n.cli import I18nCommands
    return I18nCommands(
                input_dirs={
                    'front': os.path.join(cfg_common.ROOT, 'front'),
                    'admin': os.path.join(cfg_common.ROOT, 'admin'),
                    # iktomi translations should be in iktomi itself
                    'iktomi-forms': [
                        os.path.join(IKTOMI_DIR, 'forms'),
                        os.path.join(IKTOMI_DIR, 'templates/jinja2/templates'),
                    ],
                    'iktomi-cms': os.path.join(IKTOMI_DIR, 'cms'),
                },
                output_dir=cfg_common.I18N_TRANSLATIONS_DIR,
                languages={
                    'front': ['ru', 'en'],
                    'admin': 'ru',
                    'iktomi-forms': ['ru', 'en'],
                    'iktomi-cms': 'ru',
                },
                mapping_file=cfg_common.I18N_MAPPING_FILE,
                reference_dir=cfg_common.ROOT)


@LazyCli
def err_command():
    from front.error_pages import ErrorPages
    return ErrorPages()

@LazyCli
def admin_command():
    import admin
    from iktomi.cli.app import App

    root = cfg_common.ROOT
    return App(admin.wsgi_app,
               shell_namespace={'db': admin.db_maker()},
               extra_files=[os.path.join(root, 'cfg_local.py'),
                            os.path.join(root, 'front', 'cfg_local.py'),
                            os.path.join(root, 'admin', 'cfg_local.py')])

@LazyCli
def front_command():
    import front
    from iktomi.cli.app import App

    root = cfg_common.ROOT
    return App(front.wsgi_app, 
               shell_namespace={'db': front.db_maker()},
               extra_files=[os.path.join(root, 'cfg_local.py'),
                            os.path.join(root, 'front', 'cfg_local.py')])

@LazyCli
def admin_fcgi_command():
    import admin
    from iktomi.cli.fcgi import Flup
    return Flup(admin.wsgi_app, **admin.cfg.FLUP_ARGS)

@LazyCli
def front_fcgi_command():
    import front
    from iktomi.cli.fcgi import Flup
    return Flup(front.wsgi_app, **front.cfg.FLUP_ARGS)


def run(args=sys.argv):
    manage(dict(
        # sqlalchemy session
        db = db_command,
        i18n = i18n_command,
        err = err_command,

        # dev-server
        admin = admin_command,
        front = front_command,
 
        admin_fcgi = admin_fcgi_command,
        front_fcgi = front_fcgi_command,
    ), args)


if __name__ == '__main__':
    logging.basicConfig(
            #format='%(asctime)s: %(levelname)-5s: %(name)-15s: %(message)s',
            format='%(name)-15s: %(message)s',
            level=logging.DEBUG)
    logging.getLogger('iktomi.templates').setLevel(logging.WARNING)
    logging.getLogger('iktomi.auth').setLevel(logging.WARNING)
    logging.getLogger('iktomi.web.filters').setLevel(logging.WARNING)
    logging.getLogger('iktomi.web.url_templates').setLevel(logging.WARNING)
    logging.getLogger('chakert.langs.ru').setLevel(logging.ERROR)
    logging.getLogger('chakert.langs.en').setLevel(logging.ERROR)
    run()
