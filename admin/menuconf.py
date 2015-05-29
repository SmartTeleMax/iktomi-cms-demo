# -*- coding: utf-8 -*-
from iktomi.cms.menu import Menu, MenuGroup, LangStreamMenu, \
        DashRow, DashCol, DashI18nStream, DashStream, DashI18nLoner,\
        StreamMenu


def I18nStreamMenu(*args, **kwargs):
    return MenuGroup([LangStreamMenu(*args, **dict(kwargs, lang=lang))
                      for lang in ('ru', 'en')],
                     template="menu/stream-menu-i18n")

def top_menu(env):

    return Menu(None, items=[
        Menu(u'Начало', endpoint='index'),
        I18nStreamMenu('docs', create=False),
        Menu(u'Медиа', items=[
            I18nStreamMenu('multimedia.photo_sets'),
            I18nStreamMenu('multimedia.photos'),
        ]),
        StreamMenu('admins'),
    ], env=env)


def dashboard(env):
    return MenuGroup([
        DashRow([
            DashCol(u'Сайт', items=[
                DashI18nStream('docs'),
                DashI18nStream('sections'),
                DashI18nStream('terms'),
                DashI18nStream('files'),
            ]),
            DashCol(u'Мультимедиа', items=[
                DashI18nStream('multimedia.photos'),
                DashI18nStream('multimedia.photo_sets'),
                DashI18nStream('multimedia.photo_sources'),
                DashI18nStream('multimedia.galleries'),
            ])
        ]),

        DashRow([
            DashCol(u'Главная страница', items=[
                DashI18nLoner('face_news'),
            ]),
            DashCol(u'Администрирование', items=[
                DashStream('admins'),
            ]),
       ]),


    ], env=env)
