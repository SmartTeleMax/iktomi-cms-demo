# -*- coding: utf-8 -*-

from iktomi.utils import cached_property
from models.admin import ObjectTray, Tray, AdminUser
from .menuconf import top_menu


class Context(object):

    def __init__(self, env):
        self.env = env

    @cached_property
    def top_menu(self):
        return top_menu(self.env)

    def item_trays(self, stream, item):
        return self.env.db.query(ObjectTray)\
                          .filter_by(stream_name=stream.uid(self.env, version=False),
                                     object_id=item.id).all()

    @cached_property
    def users(self):
        return self.env.db.query(AdminUser).filter_by(active=True).all()

    @cached_property
    def user_tray(self):
        user = self.env.user
        tray = self.env.db.query(Tray).filter_by(editor=user).first()
        if tray is None:
            tray = Tray(editor=user, title=user.name or user.login)
            self.env.db.add(tray)
            self.env.db.commit()
        return tray

