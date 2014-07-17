# -*- coding: utf-8 -*-

from cfg_common import *

from os import path
import memcache
import iktomi.templates, iktomi.cms
import sys
import front


SITE_DIR = path.dirname(path.abspath(__file__))
IKTOMI_TEMPLATE_DIR = path.dirname(path.abspath(iktomi.templates.__file__))
IKTOMI_CMS_DIR = path.dirname(path.abspath(iktomi.cms.__file__))
FRONT_DIR = path.dirname(path.abspath(front.__file__))

TEMPLATES = [
    path.join(SITE_DIR, 'templates'),
    path.join(IKTOMI_CMS_DIR, 'templates'),
    path.join(IKTOMI_TEMPLATE_DIR, 'jinja2', 'templates'),
]

STATIC = path.join(SITE_DIR, 'static')
STATIC_URL = '/static/'
CMS_STATIC = path.join(IKTOMI_CMS_DIR, 'static')
CMS_STATIC_URL = '/cms-static/'
MEDIA_URL = '/media/'
FRONT_STATIC = path.join(FRONT_DIR, 'static')
FRONT_STATIC_URL = '/front-static/'

FORM_TEMP = path.join(ROOT, 'data/admin/form-temp')
FORM_TEMP_URL = '/form-temp/'

TEMPLATE_IMPORT_SETTINGS = ['STATIC_URL', 'CMS_STATIC_URL']

def db_uri(db, user='demo_admin', password='demo_admin',
           host='localhost'):
    return 'mysql://{user}:{password}@{host}/{db}?charset=utf8'\
                                                .format(**locals())

DATABASES = {
    'admin': db_uri('demo_admin'),
    'front': db_uri('demo_front'),
}

DATABASE_PARAMS = {
    'pool_size': 10,
    'max_overflow': 50,
    'pool_recycle': 3600,
}

CACHE = memcache.Client(['127.0.0.1:11211'])
RAW_JS = RAW_CSS = False
MODEL_LOCK_TIMEOUT = 5*60
MODEL_LOCK_RENEW = 60

# Do not change defaults, overwrite params in FASTCGI_PARAMS instead
FASTCGI_PREFORKED_DEFAULTS = dict(
    preforked=True,
    multiplexed=False,
    minSpare=1,
    maxSpare=5,
    maxChildren=50,
    maxRequests=0,
)

FASTCGI_PARAMS = dict(
    FASTCGI_PREFORKED_DEFAULTS,
    maxSpare=8,
    minSpare=8,
    maxChildren=2,
)

FLUP_ARGS = dict(
    fastcgi_params = FASTCGI_PARAMS,
    umask = 0,
    bind = path.join(RUN_DIR, 'admin.sock'),
    pidfile = path.join(RUN_DIR, 'admin.pid'),
    logfile = path.join(LOG_DIR, 'admin.log'),
)

from collections import OrderedDict
MANIFESTS = OrderedDict([
    ("cms", {
        "path": CMS_STATIC,
        "url": CMS_STATIC_URL,
        "css": 'css/Manifest',
        "js": 'js/Manifest'
    }),
    ("", {
        "path": STATIC,
        "url": STATIC_URL,
        "css": 'css/Manifest',
        "js": 'js/Manifest'
    }),
])

cfg_local_file = path.join(SITE_DIR, 'cfg_local.py')
if path.isfile(cfg_local_file):
    execfile(cfg_local_file)
