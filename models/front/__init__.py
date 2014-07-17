from .base import (metadata,
                  FrontModel as BaseModel, 
                  FrontModelWithState as ModelWithState, 
                  FrontModelWithStateLanguage as ModelWithStateLanguage, 
                  FrontReplicatedModel as ReplicatedModel, \
                  )
from iktomi.cms.publishing.model import (
                  WithLanguage,
                  _FrontReplicated as _Replicated,
                  _WithState,
                  WithState)
from models.common import (
                  SolidReplicated,
                  SolidState)

db = 'front'
