# -*- coding: utf-8 -*-

class Link(object):

    def get_title(self, ref_title=True, default=None):
        if getattr(self, 'title', None):
            return self.title
        if ref_title and getattr(self, 'ref_title', None):
            return self.ref_title
        if self.ref_object is not None:
            return self.ref_object.title
        if default is not None:
            return default

    @property
    def ref_object(self, ref_title=True, default=None):
        if getattr(self, 'ref_doc', None):
            return self.ref_doc

    def get_url(self, url_for_object):
        if getattr(self, 'ref_url', None):
            return self.ref_url
        if getattr(self, 'ref_doc', None):
            return url_for_object(self.ref_doc)

    @property
    def has_url(self):
        return bool(
               getattr(self, 'ref_url', None) or
               getattr(self, 'ref_doc', None))
