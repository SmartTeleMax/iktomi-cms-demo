# -*- coding: utf-8 -*-

from iktomi.cms.ajax_file_upload import FileUploadHandler

from models.admin import EditorNote, Tray, ObjectTray, AdminUser
from menuconf import dashboard
from .streams import streams
from iktomi.cms.views import PostNote, TrayView
from iktomi.cms.publishing.views import PublishQueue
from iktomi.cms.packer import StaticPacker

from iktomi.cms.views import IndexHandler, \
                             update_lock, force_lock, release_lock


__all__ = ['index', 'packer',
           'update_lock', 'force_lock',
           'release_lock', 'load_tmp_image']

index = IndexHandler(dashboard)
index.func_name = 'index' # XXX

load_tmp_image = FileUploadHandler()
publish_queue = PublishQueue(streams)


packer = StaticPacker()

post_note = PostNote(EditorNote)
post_note.func_name = 'post_note' # XXX

tray_view = TrayView(Tray, ObjectTray, AdminUser)
