# -*- coding: utf-8 -*-
from iktomi import web
from iktomi.web.reverse import Location
from iktomi.web.url import URL
from webob.exc import HTTPMovedPermanently, HTTPSeeOther, HTTPMethodNotAllowed,\
        HTTPNotFound
from webob import Response
from i18n.lang import Lang


class fix_slash_match(web.match):

    def match(self, env, data):
        path = env._route_state.path
        s_request, s_match = path.endswith('/'), self.url.endswith('/')
        if s_request and not s_match:
            matched, kwargs = self.builder.match(path.rstrip('/'), env=env)
            if matched is not None:
                url = URL.from_url(env.request.url)
                url = url._copy(path=url.path.rstrip('/'))
                return HTTPMovedPermanently(location=url)
        elif not s_request and s_match:
            matched, kwargs = self.builder.match(path + '/', env=env)
            if matched is not None:
                url = URL.from_url(env.request.url)
                url = url._copy(path=url.path + '/')
                return HTTPMovedPermanently(location=url)
        else:
            return web.match.__call__(self, env, data)
    __call__ = match # for beautiful tracebacks



class guard(web.WebHandler):
    '''
        params:    None - do not check anything
                         dict - {key: type}

        methods:  if request.method not in methods, throws MethodNotAllowed
    '''

    def __init__(self, methods=('GET',), params=()):
        if params is not None:
            params = dict(params)
        self.params = params

        methods = list(methods)
        if 'GET' in methods and not 'HEAD' in methods:
            methods.append('HEAD')
        self.methods = methods

    def guard(self, env, data):
        # XXX a syntax for multiple attributes
        request = env.request
        if request.method not in self.methods:
            raise HTTPMethodNotAllowed()
        if self.params is not None:
            checked_args = set()
            for key, value in request.GET.items():
                if key.startswith('utm_'):
                    continue
                if key in checked_args or key not in self.params:
                    raise HTTPNotFound()
                checked_args.add(key)
                tp = self.params[key]
                if type(tp) in (list, tuple):
                    if not value in tp:
                        raise HTTPNotFound
                elif tp is not None and tp!="":
                    try:
                        tp(value)
                    except ValueError: # XXX write validation
                        raise HTTPNotFound()
        return self.next_handler(env, data)
    __call__ = guard


def GuardedRule(path, handler, methods=('GET',), params=(),
                name=None, convs=None):
    # werkzeug-style Rule
    if name is None:
        name = handler.func_name
    h = fix_slash_match(path, name)
    return h | guard(methods, params) | handler


Rule = GuardedRule

class DomainLocation(Location):
    def build_subdomians(self, reverse):
        subdomain = Location.build_subdomians(self, reverse)
        domain = reverse._bound_env.matched_domain
        return ".".join(filter(None, [subdomain, domain]))


class domain(web.WebHandler):
    '''
        Root domain matcher. Tryes to match the request domain by ones listed,
        in cfg and if there is no match, guesses current root domain based on
        nested subdomains in url map. It tryes to apply subdomains from url map
        to any level of requested domain.
    '''

    def __init__(self):
        web.WebHandler.__init__(self)

    def domain(self, env, data):
        request_domain = env._route_state.subdomain
        DOMAINS = env.cfg.DOMAINS
        for domain in DOMAINS:
            # match domains listed in DOMAINS
            slen = len(domain)
            delimiter = request_domain[-slen - 1:-slen]
            matches = request_domain.endswith(domain) and \
                delimiter in ('', '.')
            if matches:
                env.matched_domain = domain
                break
        else:
            # no matches in DOMAINS, try to guess matched domain based
            # on subdomain list
            # save matched domain, later it will be used in reverse
            env.matched_domain = request_domain
            for subd in self.subdomains(env):
                matched = None
                # if request domain contains subdomain, we guess that the rest
                # domain is our base domain
                if request_domain.startswith(subd+'.'):
                    matched = request_domain[len(subd)+1:]
                pos = request_domain.rfind('.'+subd+'.')
                if pos != -1:
                    matched = request_domain[pos+len(subd)+2:]
                if matched and len(matched) < len(env.matched_domain):
                    env.matched_domain = matched

        # mark base domain matched, so next subdomain filter works only with
        # remaining domain part
        env._route_state.add_subdomain(env.matched_domain, env.matched_domain)
        return self.next_handler(env, data)
    __call__ = domain

    def subdomains(self, env):
        if not hasattr(self, '_subdomains'):
            self._subdomains = self._collect_subdomains(env.root._location,
                                                        env.root._scope)
        return self._subdomains

    def _collect_subdomains(self, location, scope):
        # XXX does not work with aliases!!!
        collected = set()
        if location and location.subdomains:
            subdomain = location.subdomains[-1]
            if hasattr(subdomain, 'subdomains'):
                for s in subdomain.subdomains:
                    if s:
                        collected.add(s)
                    elif s is None and scope:
                        for loc, sc in scope.values():
                            collected |= self._collect_subdomains(loc, sc)
            else:
                collected.add(subdomain)
        elif scope:
            for loc, sc in scope.values():
                collected |= self._collect_subdomains(loc, sc)
        return collected

    def _locations(self):
        locations = super(domain, self)._locations()
        new_locations = {}
        for key, (location, scope) in locations.items():
            location = DomainLocation(*location.builders,
                                      subdomains=location.subdomains)
            new_locations[key] = (location, scope)
        return new_locations


class LangLocation(Location):

    def __init__(self, *builders, **kwargs):
        self.langs = kwargs.pop('langs')
        Location.__init__(self, *builders, **kwargs)

    def __repr__(self):
        return '%s(*%r, subdomains=%r, langs=%r)' % (
                self.__class__.__name__, self.builders,
                self.subdomains, list(self.langs))


class LangFilter(web.WebHandler):

    def __init__(self, lang_names, lang):
        self.lang_names = lang_names
        self.lang = lang

    def _filter_locations(self, _locations):
        # recursively filter out LangLocation-s without
        # selected language
        return dict([(nm, (loc, self._filter_locations(scope)))
                     for (nm, (loc, scope)) in _locations.items()
                     if not isinstance(loc, LangLocation)
                        or self.lang in loc.langs])

    def _locations(self):
        locations = web.WebHandler._locations(self)
        return self._filter_locations(locations)

    def lang_filter(self, env, data):
        env.models = getattr(env.models, self.lang)
        env.langs = [Lang(env, n) for n in self.lang_names]
        for lang in env.langs:
            if lang==self.lang:
                env.lang = data.lang = lang
                env.url_for = lang.url_for
                return self.next_handler(env, data)
        raise RuntimeError('Language %s is not provided' % self.lang)
    __call__ = lang_filter


def lang_domains(*names):
    '''Returns filter that sets namespace and `lang` parameter in `env` and
    `data` from domain name prefix.
        @langs — recognized languages, first is used by default.
    Example:
        app = environment | lang_domains('ru', 'en') | …
    '''

    def lang_domain(name, default=False):

        h = web.namespace(name) | LangFilter(names, name)
        if default:
            return web.subdomain(name, None, primary=None) | h
        return web.subdomain(name) | h

    handlers = [lang_domain(n) for n in names[1:]]
    handlers.append(lang_domain(names[0], default=True))
    return web.cases(*handlers)


class for_langs(web.WebHandler):
    '''Returns filter that uses this branch for @langs only'''

    def __init__(self, *langs):
        self.langs = frozenset(langs)

    def lang(self, env, data):
        env.allowed_languages = self.langs
        if env.lang in self.langs:
            return self.next_handler(env, data)
    __call__ = lang

    def _locations(self):
        # XXX hack (may be simply set loc.langs = self.langs,
        #           not change a class?? But it is also a hack..)
        # iterate over nested locations and change their class
        # to LangLocation, which store all appropriate languages
        locations = web.WebHandler._locations(self)
        new_locations = {}
        for name, (loc, scope) in locations.items():
            cls = loc.__class__
            assert cls in (Location, AliasLocation), \
                'for_lang sublocations class should be exact Location '\
                'otherwise we can not be shure that location class change '\
                'brakes nothing {}'.format(loc.__class__.__name__)
            if cls == AliasLangLocation:
                loc = AliasLangLocation(loc.name, loc.kwargs, langs=self.langs)
            else:
                loc = LangLocation(*loc.builders, 
                      **{'subdomains': loc.subdomains,
                         'langs': self.langs})
            new_locations[name] = (loc, scope)
        return new_locations


class alias_to_child(web.WebHandler):

    def __init__(self, _name, **kwargs):
        self.name = _name
        self.kwargs = kwargs

    def alias_to_child(self, env, data):
        if env._route_state.path:
            return None
        url_name = env.current_location+'.'+self.name
        kw = dict(data.as_dict(), **self.kwargs)
        alias = env.root.build_subreverse(url_name, **kw)
        url = str(alias)
        if getattr(env.cfg, 'DEBUG', False):
            return HTTPSeeOther(location=url)
        return HTTPMovedPermanently(location=url)
    __call__ = alias_to_child

    def _locations(self):
        return {'': (AliasLocation(self.name, self.kwargs), {})}

    def __repr__(self):
        return '%s(\'%s\')' % \
                (self.__class__.__name__, self.name)


class AliasLocation(Location):

    need_arguments = False
    url_arguments = ()
    builders = ()
    subdomains = ()

    def __init__(self, name, kwargs):
        self.name = name
        self.kwargs = kwargs

    def build_path(self, reverse, **kwargs):
        kwargs = dict(kwargs, **self.kwargs)
        alias = reverse.build_subreverse(self.name, **kwargs)
        if '' in alias._scope:
            alias = alias._finalize()
        return alias._path[len(reverse._path):]

    def build_subdomians(self, reverse):
        alias = reverse.build_subreverse(self.name, **self.kwargs)
        if '' in alias._scope:
            alias = alias._finalize()
        return alias._host[len(reverse._host):].lstrip('.')

    def __eq__(self, other):
        return self is other

    def __repr__(self):
        return '%s(\'%s\')' % (self.__class__.__name__, self.name)


class AliasLangLocation(AliasLocation):

    def __init__(self, *builders, **kwargs):
        self.langs = kwargs.pop('langs')
        AliasLocation.__init__(self, *builders, **kwargs)


def cache(seconds=None):
    @web.request_filter
    def cache_filter(env, data, next_handler):
        response = next_handler(env, data)
        if isinstance(response, Response) and \
                response.status_code // 100 == 2 and \
                env.request.method in ('GET', 'HEAD') and \
                not 'X-Accel-Expires' in response.headers:

            assert not env.request.GET # GET parameters are ignored by cache

            sec = seconds
            if sec is None:
                sec = env.cfg.DEFAULT_CACHE_DURATION
            elif isinstance(sec, basestring):
                sec = env.cfg.CACHE_DURATIONS[sec]

            response.headers['X-Accel-Expires'] = str(sec)
        return response
    return cache_filter


@web.request_filter
def nocache(env, data, next_handler):
    response = next_handler(env, data)
    if isinstance(response, Response):
        response.headers['X-Accel-Expires'] = '0'
    return response

