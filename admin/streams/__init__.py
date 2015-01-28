# -*- coding: utf-8 -*-

from iktomi.cms.stream_app import Streams
from admin.loners import loners

streams_tree = [
    'admins',
    'docs',
    'sections',
    'files',
    ['multimedia',
        'photos',
        'photo_sets',
        'photo_sources'],
    'terms',
]


streams = Streams.from_tree(streams_tree, __package__)
streams.update(loners)
