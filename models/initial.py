# -*- coding: utf-8 -*-

from models.admin import AdminUser, SectionRu


def create_admin_user(db):
    wheel = AdminUser(login='wheel', id=1, name='wheel', roles=['wheel'])
    wheel.set_password('wheel')
    db.add(wheel)

    editor = AdminUser(login='editor', id=2, name='editor', roles=['editor'])
    editor.set_password('editor')
    db.add(editor)

    admin = AdminUser(login='admin', id=3, name='admin', roles=['admin'])
    admin.set_password('admin')
    db.add(admin)

    db.commit()


def create_news_sections(db):

    SECTIONS = [dict(slug='news', title_ru=u'Новости', short_title_ru='Новости',
                                  title_en=u'News', short_title_en='News',
                     state_ru=SectionRu.PUBLIC, state_en=SectionRu.PUBLIC,
                     order_position=1),
                dict(slug='articles', title_ru=u'Авторские статьи', short_title_ru='Статьи',
                                      title_en=u'Authored articles', short_title_en='Articles',
                     state_ru=SectionRu.PUBLIC, state_en=SectionRu.PRIVATE,
                     order_position=2),
                dict(slug='reports', title_ru=u'Репортажи с места событий', short_title_ru='Репортажи',
                                     title_en=u'Reports from the place', short_title_en='Reports',
                     state_ru=SectionRu.PUBLIC, state_en=SectionRu.PUBLIC,
                     order_position=3),
                ]
    for d in SECTIONS:
        ru = SectionRu(slug=d['slug'], order_position=d['order_position'],
                       title=d['title_ru'], short_title=d['short_title_ru'],
                       state=d['state_ru'])
        db.add(ru)
        ru._create_versions()
        db.flush()

        en = ru._item_version('admin', 'en')
        en.title = en._front_item.title = d['title_en']
        en.short_title = en._front_item.short_title = d['short_title_en']
        en.state = en._front_item.state = d['state_en']

        ru.has_unpublished_changes = en.has_unpublished_changes = False
        if '_front_item' in ru.__dict__:
            # XXX fix in _create_versions
            del ru._front_item
        ru._front_item.has_unpublished_changes = en._front_item.has_unpublished_changes = False

    db.commit()


def install(db):
    create_admin_user(db)
    create_news_sections(db)
