# -*- coding: utf-8 -*-
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from models.common.fields import (Column, Integer,
        editable_ordered_relation)
from .base import register_i18n_model, register_model

@register_i18n_model('BaseModel')
def FaceNewsDoc(models):

    block_id = Column(Integer,
                      ForeignKey(models.FaceNews.id, ondelete='CASCADE'),
                      nullable=False,
                      primary_key=True)
    doc_id = Column(Integer,
                    ForeignKey(models.Doc.id),
                    nullable=False,
                    primary_key=True)
    doc = relationship(models.Doc, lazy="joined")
    order_position = Column(Integer, nullable=False, default=0)


@register_model('BaseModel', '_Replicated')
def FaceNews(models):
    id = Column(Integer, primary_key=True)


@register_i18n_model('FaceNews', 'SolidReplicated')
def FaceNews(models):

    __tablename__ = None

    _docs, docs_edit, docs = \
            editable_ordered_relation(models.FaceNewsDoc, 'doc',
                                      use_property=True)

    def __unicode__(self):
        return u'Блок главных новостей'


