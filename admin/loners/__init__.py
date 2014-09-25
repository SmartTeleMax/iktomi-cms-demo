from iktomi.cms.publishing.loner import PublishLoner
from iktomi.cms.stream_app import Streams

loners = Streams.from_tree([
    'face_news',
], __package__, stream_class=PublishLoner)
