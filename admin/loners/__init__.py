from iktomi.cms.publishing.loner import PublishLoner
from iktomi.cms.stream_app import Streams

loners_tree = [
    'face_news',
    ]

loners = Streams.from_tree(loners_tree, __package__,
                           stream_class=PublishLoner)
