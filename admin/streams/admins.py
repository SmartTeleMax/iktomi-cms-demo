# -*- coding: utf-8 -*-

from models.admin import AdminUser
from iktomi.cms.streams.admins import ItemForm as BaseItemForm, list_fields

permissions = {'admin': 'rwxcd'}
Model = AdminUser

ROLES = [
    ('wheel',   u'Полный доступ'),
    ('admin',   u'Администратор'),
    ('editor',  u'Редактор'),
]

title = u"Редакторы"
list_fields # for pyflakes

class ItemForm(BaseItemForm):

    ROLES = ROLES
