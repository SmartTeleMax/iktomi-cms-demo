# -*- coding: utf-8 -*-
from sqlalchemy import ForeignKey
from ..common.fields import (Column, Integer, String, Text)
from .base import register_i18n_model
from iktomi.db.sqla.types import Html


@register_i18n_model('ModelWithStateLanguage')
def Term(models):

    if models.lang == 'ru':
        id = Column(Integer, primary_key=True)
    else:
        id = Column(Integer, ForeignKey(models.TermRu.id),
                    primary_key=True, autoincrement=False)

    title = Column(String(100), nullable=False, default='')
    summary = Column(Html(Text), nullable=False, default='')
    body = Column(Html(Text), nullable=True)

    def __unicode__(self):
        if self.id is None:
            return u'Новый термин глоссария'
        return u'Глоссарий: {}'.format(self.title)
