import re
from models.factories import model_factories
from iktomi.unstable.db.sqla.factories import LangModelProxy, ModelsProxy
import models.admin, models.front

langs = ('ru', 'en')


class LangModelProxy(LangModelProxy):

    def _repl(self, match):
        assert match.group('format')=='l', \
                'Unsupported format %r' % match.group('format')
        return self.lang

    def __mod__(self, string):
        return re.sub('%(?P<format>.)', self._repl, string)


# XXX temporary hack!
ModelsProxy.__mod__ = lambda self, obj: self.models % obj


for module in (models.admin, models.front):
    for lang in langs:
        setattr(module, lang, LangModelProxy(module, langs, lang))

model_factories.create_all(models.admin,
                           (models.admin.ru, models.admin.en))
model_factories.create_all(models.front,
                           (models.front.ru, models.front.en))

