# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy import ForeignKey
from iktomi.utils import cached_property
from models.common.fields import Column, Integer, String, Date, DateTime, \
                                 Boolean, editable_ordered_relation
from models.factories.base import register_i18n_model, register_m2m_model
from i18n.dates import format_daterange


def _main_photo(models):
    main_photo = Column(Boolean, nullable=False, default=False)


register_m2m_model('PhotoSet', 'Photo',
                   source_attr='photo_set', ordered=True,
                   target_rel_attrs={'lazy': 'joined'},
                   extra=_main_photo)


@register_i18n_model('ModelWithStateLanguage')
def PhotoSet(models):

    if models.lang == 'ru':
        id = Column(Integer, primary_key=True)
    else:
        id = Column(Integer, ForeignKey(models.PhotoSetRu.id),
                    primary_key=True, autoincrement=False)

    date = Column(DateTime, nullable=True, default=datetime.now, index=True)
    date_end = Column(Date)
    title = Column(String(1000), nullable=True)

    _photos, photos_edit, photos = editable_ordered_relation(
            models.PhotoSet_Photo, 'photo', use_property=True)

    __mapper_args__ = {'order_by': date.desc()}

    @property
    def index_photo(self):
        if self.photos:
            main_photo = filter(lambda p:p.main_photo==True, self._photos)
            if main_photo:
                return main_photo[0].photo
            else:
                return self.photos[0]
        else:
            return None

    @index_photo.setter
    def index_photo(self, value):
        for p in self._photos:
            p.main_photo = (value is not None and p.photo.id==value.id)

    @cached_property
    def date_formatted(self):
        start, end = self.date.date(), self.date_end
        return format_daterange(start, end, locale=self.models.lang)

    def __unicode__(self):
        if self.id is None:
            return u'Новая фотоподборка'
        else:
            return u'Фотоподборка ({}): {}'.format(self.id, self.title)
