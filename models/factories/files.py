# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy import ForeignKey, desc
from sqlalchemy.types import VARBINARY as VarBinary
from iktomi.unstable.db.files import PersistentFile
from iktomi.utils import cached_property
from models.common.fields import (Column, Integer, String, Date,
        ReplicatedFileProperty)
from .base import register_i18n_model


# XXX name of this class?
class AttachedFile_(PersistentFile):

    @cached_property
    def format(self):
        return self.ext.lstrip('.')


@register_i18n_model('ModelWithStateLanguage')
def AttachedFile(models):

    BASE_PATH = 'files/' + models.lang

    if models.lang == 'ru':
      id = Column(Integer, primary_key=True)
    else:
        id = Column(Integer, ForeignKey(models.AttachedFileRu.id),
                    primary_key=True, autoincrement=False)
        old_en_id = Column(Integer)

    title = Column(String(1000))
    date = Column(Date, nullable=False, default=datetime.now, index=True)
    file_name = Column(VarBinary(250))
    file_size = Column(Integer)
    file_format = Column(String(10))
    file = ReplicatedFileProperty(file_name,
                        name_template=BASE_PATH+'/{random}',
                        persistent_cls=AttachedFile_,
                        cache_properties={'format': 'file_format',
                                          'size': 'file_size'})

    __mapper_args__ = {'order_by': desc(date)}

    def __unicode__(self):
        if self.id is None:
            return u'Новый файл'
        return u'Файл: {}'.format(self.title)
