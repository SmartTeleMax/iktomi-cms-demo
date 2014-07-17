# -*- coding: utf-8 -*-
from . import cfg

from iktomi.web.app import Application

from .urls import app
from .environment import db_maker, FrontEnvironment

__all__ = ['app', 'wsgi_app', 'db_maker']

wsgi_app = Application(app, env_class=FrontEnvironment)

