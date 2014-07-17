# -*- coding: utf8 -*-
import re
from lxml import html
from lxml.etree import XMLSyntaxError
from chakert import Typograph
from urlparse import urlparse
from jinja2 import Markup
from models.common.fields import ExpandableMarkup


def inner_html(tag):
    # XXX encode/decode everywhere is really HELL
    txt = (tag.text or '')
    txt2 = ''.join([html.tostring(x, encoding='utf-8')
                    for x in tag.iterchildren()])
    return Markup(txt + txt2.decode('utf-8'))

def prepend_text(tag, text):
    # prepends text before the tag
    if text:
        parent = tag.getparent()
        self_index = parent.index(tag)
        if self_index > 0:
            # ... or to previous sibling
            el = parent.getchildren()[self_index-1]
            el.tail = (el.tail or '') + text
        else:
            # ... or to parent
            parent.text += (parent.text or '') + text

def replace_tag_by_string(tag, string):
    fragments = html.fragments_fromstring(string)#.encode('utf-8'))
    parent = tag.getparent()
    if fragments and isinstance(fragments[0], basestring):
        # append inserted fragment's text to previous element
        prepend_text(tag, fragments.pop(0))

    for child in fragments:
        parent.insert(parent.index(tag), child)

    tag.drop_tree()


class Tag(object):

    namespace = 'iktomi'

    @classmethod
    def from_doc(cls, doc, name, namespace=None):
        if namespace is None:
            namespace = cls.namespace
        # XXX is cssselect really needed here?
        return [cls(name, tag, namespace) \
                for tag in doc.xpath('//'+cls.join(namespace, name))]
                #for tag in doc.cssselect(cls.join(namespace, name))]

    def __init__(self, name, tag, namespace=None):
        self.name = name
        self.tag = tag
        if namespace is not None:
            self.namespace = namespace

    @staticmethod
    def join(namespace, name):
        if namespace is None:
            return name
        else:
            return '_'.join((namespace, name))

    @property
    def fullname(self):
        return self.join(self.namespace, self.name)

    @property
    def inner_html(self):
        return inner_html(self.tag)


class MediaTag(Tag):

    def replace(self, env, item):
        media_items = self.get_items(item)
        id = self.tag.attrib.get('item_id')
        try:
            id = int(id)
        except (TypeError, ValueError):
            self.tag.drop_tree()
            return
        for target in media_items:
            if id == target.id:
                media = env.render_to_string("tags/%s" % self.name, dict(
                                             tag=self.tag,
                                             item=item,
                                             target=target,
                                             in_body=True))
                replace_tag_by_string(self.tag, media)
                return target
        else:
            self.tag.drop_tree()

    def get_items(self, item):
        field_name = {'photo': 'photos',
                      'photoset': 'photo_sets',
                      'audio': 'audios',
                      'video': 'videos',
                      'doclink': 'link_blocks'}.get(self.name)
        if not field_name:
            return []
        return getattr(item, field_name)



class ATag(Tag):

    namespace = None

    def replace(self, env, item):
        href = self.tag.attrib.get('href')
        if href is None:
            self.tag.drop_tag()
            return
        parsed = urlparse(href)
        if parsed.scheme != 'model':
            return

        try:
            id = int(parsed.path[1:])
        except (ValueError):
            self.tag.drop_tag()
            return

        model_name = {
            'term': 'Term',
            'doc': 'Doc',
        }.get(parsed.netloc)
        Model = getattr(env.models, model_name, None)

        if Model is None:
            self.tag.drop_tag()
            return

        query = env.db.query(Model)
        if parsed.netloc == 'pravo':
            target = query.filter_by(oid=id).scalar()
        else:
            target = query.get(id)

        if target is None:
            self.tag.drop_tag()
            return

        str_tag = env.render_to_string("tags/%s" % parsed.netloc, dict(
                                tag = self.tag,
                                item=item, 
                                target=target,
                                inner_html=self.inner_html,
                                in_body=True))
        replace_tag_by_string(self.tag, str_tag)
        return target

    def get_items(self, item, key):
        return getattr(item, key)


DEFAULT_TAGS = {'photo': MediaTag,
                'video': MediaTag,
                'audio': MediaTag,
                'photoset': MediaTag,
                'doclink': MediaTag,
                #'file': MediaTag,
                'a': ATag}

def collect_replacements(env, item, body, tags=DEFAULT_TAGS,
                         typography=False):
    if not isinstance(body, ExpandableMarkup):
        return body, []
    try:
        doc = html.fragment_fromstring(body.markup, create_parent=True)
    except XMLSyntaxError:
        return body, []
    replacements = []
    for name, tag_cls in tags.items():
        tags = tag_cls.from_doc(doc, name)
        for tag in tags:
            repl = tag.replace(env, item)
            if repl is not None:
                replacements.append(repl)

    if typography:
        Typograph.typograph_tree(doc, env.lang)

    return inner_html(doc), replacements

def replace_tags(env, item, body, tags=DEFAULT_TAGS, typography=True):
    body, _ =  collect_replacements(env, item, body, tags=tags,
                                    typography=typography)
    return body

