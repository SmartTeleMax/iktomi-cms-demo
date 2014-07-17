# -*- coding: utf8 -*-

import os

ROOT = os.path.dirname(os.path.abspath(__file__))

LOG_DIR = os.path.join(ROOT, 'logs')
RUN_DIR = os.path.join(ROOT, 'run')
MEDIA_DIR = os.path.join(ROOT, 'data/media')
I18N_DIR = os.path.join(ROOT, 'i18n')
I18N_MAPPING_FILE = os.path.join(I18N_DIR, 'mapping.ini')
I18N_TRANSLATIONS_DIR = os.path.join(I18N_DIR, 'translations')
#CFG_DIR = os.path.join(ROOT, 'cfg')

SERVE_STATIC = False

cfg_local_file = os.path.join(ROOT, 'cfg_local.py')
if os.path.isfile(cfg_local_file):
    execfile(cfg_local_file)
