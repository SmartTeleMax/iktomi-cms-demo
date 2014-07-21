# -*- coding: utf-8 -*-
from webob.exc import HTTPNotFound
from functools import partial
from iktomi.utils.paginator import ModelPaginator
from iktomi import web
from front.urls.filters import Rule
from common.replace_tags import collect_replacements


class Or404(object):
    def __ror__(self, arg):
        if not arg:
            raise HTTPNotFound()
        return arg
    __or__ = __ror__
_404 = Or404()



class DocView(object):

    ON_PAGE = 20
    item_template = 'events/item.html'
    index_template = 'events/index.html'

    @property
    def index_rules(self):
        return [
            Rule('', self.index, name=''),
            Rule('/page/<int:page>', self.index, name='page'),
        ]

    @property
    def section_rules(self):
        rules = self.index_rules
        return [web.prefix('/by-section/<section_slug>', name='by_section') | \
                        web.cases(*rules)]

    @property
    def item_rules(self):
        return [Rule('/<int:id>', self.item)]

    @property
    def app(self):
        rules = self.index_rules + \
                self.section_rules + \
                self.item_rules
        return web.cases(*rules)

    @staticmethod
    def get_model(env):
        return env.models.Doc

    def get_reverse(self, env, data):
        return env.lang.root.events

    def _stream_reverse(self, env, data):
        reverse = self.get_reverse(env, data)
        section = getattr(data, 'section', None)
        if section is not None:
            reverse = reverse.by_section(section_slug=section.slug)
        return reverse

    def _stream_url(self, env, data, page):
        reverse = self._stream_reverse(env, data)
        if page > 1:
            return reverse.page(page=page)
        return reverse

    def prepare_data(self, env, data):
        Section = env.models.Section
        data.section = None

        if hasattr(data, 'section_slug'):
            data.section = _404 | env.db.query(Section)\
                                        .filter_by(slug=data.section_slug)\
                                        .first()
            env.published_items += (data.section,)

        sections = env.db.query(Section).all()
        env.template_data = dict(env.template_data,
                                 section=data.section,
                                 sections=sections,
                                 reverse=self.get_reverse(env, data),
                                 )

    def get_query(self, env, data, _query=None):
        Model = self.get_model(env)
        query = _query if _query is not None else env.db.query(Model)
        query = query.order_by(Model.date.desc())

        if data.section is not None:
            query = query.filter(Model.sections.contains(data.section))
        return query


    def index_data(self, env, data):
        docs_query = self.get_query(env, data)
        page = getattr(data, 'page', 1)
        paginator = self.paginator(env, data, docs_query, page)

        return {
            'paginator': paginator,
            'stream_reverse': self._stream_reverse(env, data),
        }

    def paginator(self, env, data, docs_query, page):
        paginator = ModelPaginator(env.request, docs_query,
                              limit=self.ON_PAGE,
                              page=page,
                              page_url=partial(self._stream_url, env, data))
        if not paginator.items:
            raise HTTPNotFound()
        return paginator

    def index(self, env, data):
        self.prepare_data(env, data)
        template_data = self.index_data(env, data)
        return env.render_to_response(self.index_template, template_data)

    def item(self, env, data):
        self.prepare_data(env, data)
        docs_query = self.get_query(env, data)

        item = _404 | docs_query.filter_by(id=data.id).first()
        env.published_items += (item,)

        extra_media = item.photo_sets + item.photos

        body, replacements = collect_replacements(env, item, item.body)
        extra_media = [x for x in extra_media
                       if not x in replacements]
        link_blocks = [x for x in item.link_blocks
                       if not x in replacements]

        return env.render_to_response(self.item_template, dict(
            item=item,
            body=body,
            extra_media=extra_media,
            link_blocks=link_blocks,
        ))



events = DocView()

