# -*- coding: utf8 -*-
from iktomi.unstable.db.sqla.factories import return_locals
import models

# XXX move to iktomi.cms

class FormVersions(dict):
    def _get_form(self, mls):
        return self[mls.db]

    def __call__(self, env, *args, **kwargs):
        return self._get_form(env.models)(env, *args, **kwargs)

    def load_initial(self, env, *args, **kwargs):
        return self._get_form(env.models).load_initial(env, *args, **kwargs)


# do not remove
def class_factory(*parents):
    def wrapper(f):
        def create_class(*args):
            ps = [(parent._get_form(*args)
                    if isinstance(parent, FormVersions)
                    else parent)
                  for parent in parents]
            cls = type(f.func_name, tuple(ps), return_locals(f)(*args))
            cls.__module__ = f.__module__
            return cls
        return FormVersions({'admin': create_class(models.admin),
                             'front': create_class(models.front)})
    return wrapper


class I18nFormVersions(FormVersions):

    def _get_form(self, mls):
        return self[mls.db+'.'+mls.lang]

class I18nNoDBFormVersions(FormVersions):

    def _get_form(self, mls):
        return self[mls.lang]


def i18n_class_factory(*parents, **kwargs):
    def wrapper(f):
        def create_class(*args):
            ps = [(parent._get_form(*args)
                    if isinstance(parent, FormVersions)
                    else parent)
                  for parent in parents]
            cls = type(f.func_name, tuple(ps), return_locals(f)(*args))
            cls.__module__ = f.__module__
            return cls
        langs = kwargs.pop('langs', ['ru', 'en'])
        versions = kwargs.pop('versions', ['admin', 'front'])
        m = kwargs.pop('models', models)
        if versions:
            forms = dict(('{}.{}'.format(version, lang),
                          create_class(getattr(getattr(m, version), lang)))
                         for lang in langs for version in versions)
            return I18nFormVersions(forms)
        else:
            forms = dict((lang,
                          create_class(getattr(m, lang)))
                         for lang in langs)
            return I18nNoDBFormVersions(forms)
    return wrapper


class ModelFormChooser(object):
    '''A simple object with ModelForm init interface to vary form classes'''
    def __init__(self, form_func):
        self.form = form_func

    def __call__(self, env, initial, item=None, **kwargs):
        return self.form(env, initial, item)(
                env, initial, item=item, **kwargs)

    def load_initial(self, env, item, initial, **kwargs):
        return self.form(env, initial, item).load_initial(
                env, item, initial=initial, **kwargs)

