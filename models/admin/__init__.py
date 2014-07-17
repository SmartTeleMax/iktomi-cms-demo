from .base import (metadata,
                   AdminModel as BaseModel,
                   AdminReplicatedModel as ReplicatedModel,
                   AdminModelWithState as ModelWithState,
                   AdminModelWithStateLanguage as ModelWithStateLanguage)
from iktomi.cms.publishing.model import (
                   AdminWithLanguage as WithLanguage,
                   _AdminReplicated as _Replicated,
                   _AdminWithState as _WithState,
                   AdminWithState as WithState)
from models.common import (
                   AdminSolidReplicated as SolidReplicated, \
                   SolidState)
from iktomi.cms.models import model_factories


db = 'admin'


class _module(object):
    def __init__(self, kwargs):
        self.__dict__.update(kwargs)
        self.dict = {}

    def __setattr__(self, key, value):
        self.__dict__[key] = value
        self.dict[key] = value


# XXX Hack!!! Other way to do this?
md = _module(locals())
model_factories.create_all(md,
    model_names=('EditorNote', 'AdminUser', 'DraftFormAdminUser', 'DraftForm',
                 'EditLogAdminUser', 'EditLog', 'ObjectTray', 'Tray'))
locals().update(md.dict)
del md; del _module
