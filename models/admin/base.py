# -*- coding: utf-8 -*-

from sqlalchemy.schema import MetaData
from sqlalchemy.ext.declarative import declarative_base
from iktomi.cms.publishing.model import AdminReplicated, AdminWithState, AdminWithLanguage
from ..base import ModelsMeta

metadata = MetaData()

AdminModel = declarative_base(metadata=metadata,
                              name='AdminModel',
                              metaclass=ModelsMeta)


class AdminReplicatedModel(AdminModel, AdminReplicated):
    '''Model that is replacated (published) to front. You always have two
    versions: current and published.
    Don't use it for secondary table models that are not replicated directly
    (use AdminModel instead).'''

    __abstract__ = True


class AdminModelWithState(AdminWithState, AdminReplicatedModel):

    __abstract__ = True


class AdminModelWithStateLanguage(AdminWithLanguage, AdminModelWithState):

    __abstract__ = True


# XXX Tracking below is commented since due to limitted time
#
#AdminModelUntracked = declarative_base(metadata=metadata,
#                                       name='AdminModelUntracked',
#                                       metaclass=DeclarativeMeta)
#
#
#class AdminChanges(AdminModelUntracked):
#
#    id = Column(Integer, primary_key=True)
#    time = Column(DateTime, nullable=False, default=datetime.now)
#    object_id = Column(String(250), nullable=False, index=True)
#    admin_user_id = Column(ForeignKey('AdminUser.id'))
#    admin_user = relation('AdminUser')
#    action = Column(String(100), nullable=False)
#    fields = Column(StringList(1000))
#    changes = Column(Text)
#
#
#class AdminModel(AdminModelUntracked):
#
#    __abstract__ = True
#    _changes_logger = ChangesLogger(AdminChanges)
#


