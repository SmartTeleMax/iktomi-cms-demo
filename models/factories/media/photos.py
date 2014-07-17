# -*- coding: utf-8 -*-

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relation
from sqlalchemy.types import VARBINARY as VarBinary
from models.common.fields import (Column, Integer, String, Date, 
        ReplicatedImageProperty)
from iktomi.unstable.utils.image_resizers import ResizeMixed, ResizeFit
from models.factories.base import register_model, register_i18n_model
from models.common.properties import ResizeCropUpper

try:
    from PIL import ImageFilter, ImageEnhance
except ImportError:
    import ImageFilter, ImageEnhance


@register_model('BaseModel', '_WithState', '_Replicated')
def PhotoSource(models):

    id = Column(Integer, primary_key=True)

    def __unicode__(self):
        if self.id is None:
            return u'Новый источник изображений'
        else:
            return u'Источник изображений ({}): {}'.format(self.id, self.title)


@register_i18n_model('PhotoSource', 'SolidState', 'SolidReplicated')
def PhotoSource(models):

    __tablename__ = None
    title = Column(models%'title_%l', String(250), nullable=True)


resizer = ResizeMixed(ResizeCropUpper(), ResizeFit())


@register_model('BaseModel', '_WithState', '_Replicated')
def Photo(models):

    BASE_PATH = 'photos'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, index=True)
    source_id = Column(Integer, ForeignKey(models.PhotoSource.id))

    image_name = Column(VarBinary(250), nullable=False)
    image_size = Column(Integer, nullable=False)
    image_width = Column(Integer, nullable=False)
    image_height = Column(Integer, nullable=False)
    image = ReplicatedImageProperty(image_name,
                        name_template=BASE_PATH+'/orig/{random}',
                        resize=ResizeFit(),
                        image_sizes=(5000, 5000),
                        cache_properties={'size': 'image_size',
                                          'width': 'image_width',
                                          'height': 'image_height'})

    image_big_name = Column(VarBinary(250), nullable=False)
    image_big = ReplicatedImageProperty(image_big_name,
                        name_template=BASE_PATH+'/big/{random}',
                        fill_from='image',
                        resize=resizer,
                        # apply brightness only to image sizes filled directly
                        # from the original image
                        enhancements=[(ImageEnhance.Brightness, 1.1)],
                        image_sizes=(1024, 632))

    image_medium_name = Column(VarBinary(250), nullable=False)
    image_medium = ReplicatedImageProperty(image_medium_name,
                        name_template=BASE_PATH+'/medium/{random}',
                        # fill from image_big, not from original, because
                        # it allows us to crop image only once
                        fill_from='image_big',
                        resize=resizer,
                        image_sizes=(680, 420))

    image_small_name = Column(VarBinary(250), nullable=False)
    image_small = ReplicatedImageProperty(image_small_name,
                        name_template=BASE_PATH+'/small/{random}',
                        fill_from='image',
                        resize=ResizeCropUpper(),
                        # apply brightness only to image sizes filled directly
                        # from the original image
                        enhancements=[(ImageEnhance.Brightness, 1.1)],
                        quality=100,
                        image_sizes=(300, 300))

    image_tiny_name = Column(VarBinary(250), nullable=False)
    image_tiny = ReplicatedImageProperty(image_tiny_name,
                        name_template=BASE_PATH+'/tiny/{random}',
                        fill_from='image_medium',
                        resize=ResizeFit(),
                        quality=100,
                        image_sizes=(130, 130))

    __mapper_args__ = {'order_by': date.desc()}

    def __unicode__(self):
        if self.id is None:
            return u'Новая фотография'
        else:
            return u'Фотография ({}): {}'.format(
                        self.id, self.title or u'(без подписи)')


@register_i18n_model('Photo', 'SolidState', 'SolidReplicated')
def Photo(models):

    __tablename__ = None

    title = Column(models%'title_%l', String(1000), nullable=True)
    place = Column(models%'place_%l', String(250), nullable=True)

    source = relation(models.PhotoSource)

