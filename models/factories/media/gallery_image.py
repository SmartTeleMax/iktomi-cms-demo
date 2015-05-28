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

resizer = ResizeMixed(ResizeCropUpper(), ResizeFit())


@register_i18n_model('ModelWithStateLanguage')
def Gallery(models):

    id = Column(Integer, primary_key=True)

    title = Column(String(100), nullable=False, default='')
    def __unicode__(self):
        if self.id is None:
            return u'Новая галерея'
        return u'Галерея: {}'.format(self.title)


@register_i18n_model('ModelWithStateLanguage')
def GalleryImage(models):

    BASE_PATH = 'gallery_images'

    id = Column(Integer, primary_key=True)
    title = Column(String(1000), nullable=True)
    gallery_id = Column(Integer, ForeignKey(models.Gallery.id))
    gallery = relation(models.Gallery, backref="images")

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
                        image_sizes=(500, 500))

    def __unicode__(self):
        if self.id is None:
            return u'Новое изображение'
        else:
            return u'Изображение ({}): {}'.format(
                        self.id, self.title or u'(без подписи)')


