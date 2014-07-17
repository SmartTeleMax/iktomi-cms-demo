# -*- coding: utf-8 -*-
from iktomi.cms.publishing.model import *
from iktomi.cms.publishing.model import _get_model_name
import sqlalchemy

# ============================== Single table models without state ==========

class _SolidReplicated(object):

    @declared_attr
    def has_unpublished_changes(self):
        '''Was the object updated after publishing? Does it differ from
        published version?'''
        return Column('has_unpublished_changes_' + self.models.lang,
                      Boolean, nullable=False, default=True,
                      server_default='0')#, onupdate=True)


class SolidReplicated(_SolidReplicated, WithLanguage):
    pass


class AdminSolidReplicated(_SolidReplicated, WithLanguage):

    def item_global_id(self):
        cls, ident = sqlalchemy.orm.util.identity_key(instance=self)
        ident = '-'.join(map(str, ident))
        modelname = _get_model_name(self)
        return '%s.%s:%s' % (cls.__module__, modelname, ident)


class SolidState(object):

    @declared_attr
    def state(self):
        return Column('state_' + self.models.lang,
                      Integer, nullable=True, default=self.ABSENT)
