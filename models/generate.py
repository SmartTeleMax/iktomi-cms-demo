# -*- coding: utf-8 -*-

from __future__ import absolute_import

from datetime import datetime, timedelta
import logging
from random import randint, choice, randrange
import sys, os

from PIL import Image as PILImage  # as we have duplicated constant, and
                                   # there is no time to fix it
from PIL import ImageDraw
from admin.environment import db_maker, file_manager
from .vesna import phrase

from models.admin import DocRu, PhotoRu, PhotoSetRu, SectionRu,\
        FaceNewsRu, FaceNewsEn, DocEn
from models.common.fields import ExpandableMarkup

logger = logging.getLogger('generate')


def _get_rand_date(since=None, to=None):
    if since is None:
        since = datetime.now() - timedelta(seconds=100 * 24 * 3600)
    if to is None:
        to = datetime.now() + timedelta(seconds=30 * 24 * 3600)
    assert since < to, 'since-date whould be less then to-date'
    delta = to - since
    shift = randrange(delta.seconds + delta.days * 24 * 3600)
    return (since + timedelta(seconds=shift)).date()


def _create_image(width=650, height=434):
    image = PILImage.new('RGB', (width, height), (randint(1, 240),
                                                  randint(1, 240),
                                                  randint(1, 240), 1))
    for x in xrange(0, randint(1, 5)):
        draw = ImageDraw.Draw(image)
        points = [(randint(1, width), randint(1, height))
                  for x in xrange(0, randint(4, 6))]
        draw.polygon(points, fill=(randint(150, 255),
                                   randint(150, 255),
                                   randint(150, 255), 1))
    return image


def _create_image_file(width=650, height=434, image=None):
    if image is None:
        image = _create_image(width=width, height=height)
    temp_image = file_manager.new_transient(".png")
    if not os.path.isdir(file_manager.transient_root):
        os.makedirs(file_manager.transient_root)
    image.save(temp_image.path, options={'quality': 90})
    return temp_image


def _set_random_stage(db, item, updater=None):
    """ updater should be a function than knows how to update item
    """

    item._create_versions()
    db.commit()

    if '_front_item' in item.__dict__:
        # XXX fix _create_versions
        del item._front_item

    item.state = item._front_item.state = item.ABSENT
    if choice((True, True, False,)):
        item.state = item._front_item.state = item.PRIVATE
        if choice((True, True, True, False,)):
            item.state = item._front_item.state = item.PUBLIC
    db.flush()


def _create_obj(db, model, title, **kwargs):
    values = {'title': title}
    values.update(kwargs)
    obj = model(**values)
    db.add(obj)
    return obj


def _random_list(arr, max_length=5, min_length=0):
    length = randint(min_length, max_length)
    return list(set([choice(arr) for i in range(0, length)]))


def photos(db, count=30):
    for i in xrange(count+1):
        img = _create_image(1200, 800)
        photo = _create_obj(db, PhotoRu, u"Фото %d" % i,
                            date = _get_rand_date(datetime(1994, 01, 01)),
                            image=_create_image_file(image=img))

        _set_random_stage(db, photo)

        en = photo._item_version('admin', 'en')
        en.date = photo.date
        _set_random_stage(db, en)
    db.commit()


def photosets(db, count=30):
    all_photos = db.query(PhotoRu).all()
    for i in xrange(count+1):
        photoset = _create_obj(db, PhotoSetRu,
                               u"Фотолента %d" % i,
                               date = _get_rand_date(datetime(1994, 01, 01)))
        photoset.photos_edit = set([choice(all_photos)
                               for i in range(0, randint(1, 10))])
        _set_random_stage(db, photoset)

        en = photoset._item_version('admin', 'en')
        en.title = 'Photo set %d' % i
        en.photos_edit = [x._item_version('admin', 'en')
                          for x in photoset.photos]
        en.date = photoset.date
        _set_random_stage(db, en)
        en._copy_to_front()
    db.commit()


def docs(db, count=30):
    all_photos = db.query(PhotoRu).all()
    all_photo_sets = db.query(PhotoSetRu).all()
    all_sections = db.query(SectionRu).all()


    for i in xrange(count+1):
        title = phrase()[:randint(30, 100)]

        summary = phrase()[:randint(100, 300)]
        body = "<p>%s</p><p>%s</p>" % (phrase()[:10], phrase())
        doc = _create_obj(db, DocRu, title,
                          summary=summary,
                          body=ExpandableMarkup(body))

        doc.date = _get_rand_date(datetime(1994, 01, 01), doc.date)

        doc.photo_sets_edit = _random_list(all_photo_sets, 2)
        doc.photos_edit = _random_list(all_photos, 3)
        doc.sections = _random_list(all_sections, 3, 1)
        db.add(doc)
        _set_random_stage(db, doc)

        en = doc._item_version('admin', 'en')
        en.date = doc.date
        en.title = phrase()[:randint(30, 100)]
        en.summary = phrase()[:randint(100, 300)]
        en.body=ExpandableMarkup("<p>%s</p><p>%s</p>" % (phrase()[:10], phrase()))
        en.photo_sets_edit = [x._item_version('admin', 'en') for x in doc.photo_sets]
        en.photos_edit = [x._item_version('admin', 'en') for x in doc.photos]
        en.sections = [x._item_version('admin', 'en') for x in doc.sections]
        _set_random_stage(db, en)

        en._copy_to_front()

        db.commit()

    all_docs_ru = db.query(DocRu).all()
    all_docs_en = db.query(DocEn).all()

    face_ru = db.query(FaceNewsRu).one()
    face_ru.docs_edit = _random_list(all_docs_ru, 3, 3)
    face_ru.publish()

    face_en = db.query(FaceNewsEn).one()
    face_en.docs_edit = _random_list(all_docs_en, 3, 3)
    face_en.publish()


generators = {
    'photos': photos,
    'photosets': photosets,
    'docs': docs,
}



if __name__ == '__main__':
    names = generators
    if len(sys.argv) > 1:
        for name in sys.argv[1:]:
            if name not in generators:
                print 'Incorrect generator name "%s"' % name
                sys.exit(1)
        names = sys.argv[1:]
    for name in names:
        print name
        generators[name](db_maker())

