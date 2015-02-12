# -*- coding: utf-8 -*-
import collections
from datetime import datetime
from sqlalchemy import ForeignKey, desc
from sqlalchemy.orm import relationship, deferred
from sqlalchemy.ext.orderinglist import ordering_list
from ..common.fields import (Column, Integer, String, DateTime,
        Text, MediumText, Html, ExpandableHtml, ExpandableMarkup,
        Boolean)
from ..common.properties import FilteredProperty
from ..common.fields import editable_ordered_relation
from .base import register_i18n_model, register_m2m_model
from .mixins import Link
from iktomi.utils import cached_property
from i18n.dates import format_datetime


register_m2m_model('Doc', 'Photo', ordered=True)
register_m2m_model('Doc', 'PhotoSet', target_attr='photo_set', ordered=True)
register_m2m_model('Doc', 'Section', target_attr='section')


@register_i18n_model('BaseModel', Link)
def DocLink(models):

    id = Column(Integer, primary_key=True)
    order_position = Column(Integer, nullable=False, default=0)
    block_id = Column(Integer,
                      ForeignKey(models.DocLinkBlock.id, ondelete='CASCADE'),
                      nullable=False)
    block = relationship(lambda: models.DocLinkBlock,
                     primaryjoin=(lambda: block_id==models.DocLinkBlock.id))

    ref_title = Column(String(500), default='')
    ref_url = Column(String(250), nullable=True)
    ref_doc_id = Column(Integer, ForeignKey(models.Doc.id))
    ref_doc = relationship(models.Doc,
                       primaryjoin=(lambda: ref_doc_id==models.Doc.id))

    def __unicode__(self):
        return u"Ссылка: {}".format(self.get_title())


@register_i18n_model('BaseModel')
def DocLinkBlock(models):
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False, default='')
    doc_id = Column(Integer, ForeignKey(models.Doc.id, ondelete='CASCADE'),
                    nullable=False)
    doc = relationship(models.Doc)

    links_edit = relationship(models.DocLink,
                      collection_class=ordering_list('order_position'),
                      order_by=[models.DocLink.order_position],
                      cascade='all, delete-orphan')
    # do not display links which can not be transformed to urls,
    # for example links to unpublished documents
    links = FilteredProperty('links_edit', has_url=True)
    order_position = Column(Integer, nullable=False, default=0)

    @property
    def has_links(self):
        return bool(self.links)

    def __unicode__(self):
        return u"Блок ссылок: {}".format(self.title)


@register_i18n_model('ModelWithStateLanguage')
def Doc(models):

    if models.lang == 'ru':
        id = Column(Integer, primary_key=True)
    else:
        id = Column(Integer, ForeignKey(models.DocRu.id),
                    primary_key=True, autoincrement=False)

    date = Column(DateTime, nullable=False, default=datetime.now, index=True)
    title = Column(Html(String(1000)), nullable=False, default='')

    summary = Column(Html(Text), nullable=False, default='')
    body = deferred(Column(ExpandableHtml(MediumText), nullable=False,
                    default=ExpandableMarkup('')))

    _photos, photos_edit, photos = editable_ordered_relation(
            models.Doc_Photo, 'photo', use_property=False)
    _photo_sets, photo_sets_edit, photo_sets = editable_ordered_relation(
            models.Doc_PhotoSet, 'photo_set', use_property=False)

    link_blocks_edit = relationship(
            models.DocLinkBlock,
            order_by=[models.DocLinkBlock.order_position],
            collection_class=ordering_list('order_position'),
            cascade='all, delete-orphan')
    # do not display blocks without links
    link_blocks = FilteredProperty('link_blocks_edit', has_links=True)

    sections = relationship(
            models.Section,
            secondary=models.Doc_Section.__table__)

    on_main = Column(Boolean, nullable=False, default=True)

    __mapper_args__ = {'order_by': desc(date)}

    def __unicode__(self):
        if self.id is None:
            return u'Новый материал'
        return u'Материал: {}'.format(self.title)

    @cached_property
    def index_photo(self):
        if self.photos:
            return self.photos[0]
        elif self.photo_sets:
            return self.photo_sets[0].index_photo
        else:
            return None

    @cached_property
    def all_photos(self):
        photos = sum([x.photos for x in self.photo_sets], []) + self.photos
        return list(collections.OrderedDict.fromkeys(photos))

    @cached_property
    def links_count(self):
        return sum([len(x.links) for x in self.link_blocks])

    @cached_property
    def date_formatted(self):
        return format_datetime(self.date, locale=self.models.lang)

