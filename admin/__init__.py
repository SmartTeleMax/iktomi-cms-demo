# -*- coding: utf-8 -*-

from iktomi.web.app import Application
from .urls import app
from .environment import db_maker, AdminEnvironment

__all__ = ['app', 'wsgi_app', 'db_maker']

wsgi_app = Application(app, env_class=AdminEnvironment)

