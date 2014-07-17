# -*- coding: utf-8 -*-

from sqlalchemy.schema import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from iktomi.cms.publishing.model import FrontReplicated, WithState, WithLanguage,\
        FrontOnlyWithState
from ..base import ModelsMeta

metadata = MetaData()

FrontModel = declarative_base(metadata=metadata,
                              name='FrontModel',
                              metaclass=ModelsMeta)


class FrontReplicatedModel(FrontModel, FrontReplicated):
    '''Model that is replacated (published) from admin. You always have two
    versions: current and published.
    Don't use it for secondary table models that are not replicated directly
    (use FrontModel instead).'''

    __abstract__ = True


class FrontModelWithState(FrontReplicatedModel, WithState):

    __abstract__ = True

    @hybrid_property
    def public(self):
        return self.state == self.PUBLIC

    @public.expression
    def public(cls):
        return cls.state == cls.PUBLIC


class FrontModelWithStateLanguage(WithLanguage, FrontModelWithState):

    __abstract__ = True


class FrontOnlyWithState(FrontModel, FrontOnlyWithState):

    __abstract__ = True
