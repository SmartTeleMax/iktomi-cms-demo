# -*- coding: utf-8 -*-

from cfg_common import *

from os import path
import memcache
import sys


SITE_DIR = path.dirname(path.abspath(__file__))

TEMPLATES = [
    path.join(SITE_DIR, 'templates'),
]

STATIC = path.join(SITE_DIR, 'static')
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

TEMPLATE_IMPORT_SETTINGS = ['STATIC_URL', 'PREVIEW']

def db_uri(db, user='demo_front', password='demo_front',
           host='localhost'):
    return 'mysql://{user}:{password}@{host}/{db}?charset=utf8'\
                                                .format(**locals())

DATABASES = {
    'front': db_uri('demo_front'),
}

DATABASE_PARAMS = {
    'pool_size': 10,
    'max_overflow': 50,
    'pool_recycle': 3600,
}

# XXX move to code?
CACHE = memcache.Client(['127.0.0.1:11211'])
DOMAINS = []
CACHE_PAGES_ENABLED = True
RAW_JS = RAW_CSS = False
PREVIEW = False

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
    bind = path.join(RUN_DIR, 'front.sock'),
    pidfile = path.join(RUN_DIR, 'front.pid'),
    logfile = path.join(LOG_DIR, 'front.log'),
)

cfg_local_file = path.join(SITE_DIR, 'cfg_local.py')
if path.isfile(cfg_local_file):
    execfile(cfg_local_file)
