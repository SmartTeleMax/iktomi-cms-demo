# -*- coding: utf-8 -*-

from models.common.properties import OrderColumn
from models.common.fields import (Column, Integer, String)
from models.factories.base import register_model, register_i18n_model


@register_model('BaseModel', '_WithState', '_Replicated')
def Section(models):

    id = Column(Integer, primary_key=True)
    slug = Column(String(50))
    order_position = OrderColumn(Integer, nullable=False)

    def __unicode__(self):
        if self.id is None:
            return u'Новый раздел'
        return u'Раздел: {}'.format(self.title)


@register_i18n_model('Section', 'SolidState', 'SolidReplicated')
def Section(models):

    __tablename__ = None

    title = Column(models%'title_%l', String(1000), nullable=True)
    short_title = Column(models%'short_title_%l', String(250), nullable=True)


