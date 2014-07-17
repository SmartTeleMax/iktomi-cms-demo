# -*- coding: utf-8 -*-
import json
from webob import Request
from iktomi import web
from iktomi.utils.storage import VersionedStorage
from iktomi.cms.publishing.model import AdminPublicQuery
from front import wsgi_app
from i18n.lang import Lang


@web.request_filter
def set_models(env, data, nxt):
    #assert data.version in self.versions_dict.keys()
    env.models = getattr(env.models, data.version)
    env.models = getattr(env.models, data.lang)
    env.version = data.version
    env.lang = data.lang
    return nxt(env, data)


def call_with_front_env(env, data, nxt):

    request = Request.blank(env._route_state.path+'?'+env.request.query_string,
                            charset='utf-8')
    front_env = VersionedStorage(wsgi_app.env_class, request, wsgi_app.root)
    # env.root is created in wsgi_app, we do not wrap front app in one,
    # so we have to create env.root manually
    front_env.root = env.root.front(version=env.version, lang=env.lang)\
                             .bind_to_env(front_env)
    front_env.models = env.models
    # we wave set language explicitly here, because language detection is based
    # on subdomains, and we do not have ones in admin
    front_env.langs = [Lang(front_env, n) for n in ['en', 'ru']]
    front_env.lang = [x for x in front_env.langs if x == env.lang][0]
    front_env.matched_domain = ''
    front_env.db = env.db
    front_data = VersionedStorage()
    front_env.data = front_data

    # XXX hack to make cfg configurable
    _cfg = front_env.cfg
    front_env.cfg = VersionedStorage()
    front_env.cfg._storage._parent_storage = _cfg
    _cfg._parent_storage = None

    front_env.cfg.STATIC_URL = env.cfg.FRONT_STATIC_URL
    front_env.cfg.PREVIEW = True
    front_env.cfg.DOMAINS = [env.request.host.split(':', 1)[0]]
    old_query = front_env.db._query_cls
    try:
        query_cls = AdminPublicQuery# if env.version == 'admin' else PublicQuery
        # XXX hack!
        front_env.db._query_cls = query_cls
        return nxt(front_env, front_data)
    finally:
        front_env.db._query_cls = old_query


@web.request_filter
def collect_unpublished(env, data, nxt):
    result = nxt(env, data)
    unpublished = []
    for obj in env.db.identity_map.values():
        if (isinstance(obj, env.models._WithState) or
            isinstance(obj, env.models.WithState)) and \
                obj.state == obj.PRIVATE:
            unpublished.append({'title': unicode(obj)})
    if unpublished:
        script = '''<head><script>
            if(window.parent){
                window.parent.unpublishedItems(%s)
            }
        </script>'''% json.dumps(unpublished)
        result.body = script.join(result.body.split('<head>',1));
    return result

front_environment = set_models | web.request_filter(call_with_front_env) | collect_unpublished
