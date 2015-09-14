# -*- coding: utf-8 -*-

from models.admin import EditorNote, Tray, ObjectTray, AdminUser
from menuconf import dashboard
from .streams import streams
from iktomi.cms.editor_notes.views import PostNote
from iktomi.cms.tray.views import TrayView
from iktomi.cms.publishing.views import PublishQueue
from iktomi.cms.packer import StaticPacker

from iktomi.cms.menu import IndexHandler
from iktomi.cms.item_lock.views import ItemLockView


__all__ = ['index', 'packer',
           'update_lock', 'force_lock',
           'release_lock', 'load_tmp_image']

index = IndexHandler(dashboard)
index.func_name = 'index' # XXX

publish_queue = PublishQueue(streams)


packer = StaticPacker()

post_note = PostNote(EditorNote)
post_note.func_name = 'post_note' # XXX

tray_view = TrayView(Tray, ObjectTray, AdminUser)
item_lock_view = ItemLockView()
