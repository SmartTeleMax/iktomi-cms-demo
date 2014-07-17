from iktomi.cms.publishing.loner import PublishLoner
from iktomi.cms.stream_app import Loners

loners = Loners.from_tree([
    'face_news',
], __package__, loner_class=PublishLoner)
