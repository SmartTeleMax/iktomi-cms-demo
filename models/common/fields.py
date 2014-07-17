from sqlalchemy import (Column, Integer, DateTime, String, Text, Enum,
                        PrimaryKeyConstraint, ForeignKey, desc, Date,
                        Boolean, types)
from sqlalchemy.orm import relation
from sqlalchemy.dialects.mysql import (MEDIUMTEXT as MediumText,
                                       LONGTEXT as LongText)
from iktomi.cms.publishing.files import (
        ReplicatedFileProperty, ReplicatedImageProperty)
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.orderinglist import ordering_list
from iktomi.db.sqla.types import Html
from jinja2 import Markup

# for pyflakes
(Column, Integer, DateTime, String, Text, Enum,
 PrimaryKeyConstraint, ForeignKey, desc, Date,
 Boolean, types, ReplicatedFileProperty, ReplicatedImageProperty)


HtmlMediumText = Html(MediumText)


def ordered_relation(Model):
    return relation(Model,
                    order_by=Model.order_position,
                    collection_class=ordering_list('order_position'),
                    cascade='all, delete-orphan')


def ordered_relation_proxy(Model, target, attr):
    return association_proxy(target, attr,
                             creator=lambda item: Model(**{attr: item}))

def editable_ordered_relation(SecondaryModel, prop, use_property=True):
    _prop = ordered_relation(SecondaryModel)

    prop_edit = association_proxy(
                    '_' + prop + 's', prop,
                    creator=lambda item: SecondaryModel(**{prop: item}))

    if use_property:
        @property
        def props(self):
            return [p for p in getattr(self, prop+'s_edit')
                    if p is not None]
    else:
        props = relation(
                # XXX is this ok?
                getattr(SecondaryModel, prop).comparator.prop.argument,
                secondary=SecondaryModel.__table__,
                order_by=[SecondaryModel.order_position],
                viewonly=True)

    return _prop, prop_edit, props


class ExpandableMarkup(object):
    '''
        Wrapper for markup which should be preprocessed on front-end.
    '''

    def __init__(self, markup):
        if isinstance(markup, ExpandableMarkup):
            self.markup = markup.markup
        else:
            self.markup = Markup(markup)

    def __len__(self):
        return len(self.markup)

    def __unicode__(self):
        raise RuntimeError('ExpandableMarkup is not converted and '
                           'can not be displayed')
    __html__ = __str__ = __unicode__

    def __eq__(self, other):
        if isinstance(other, ExpandableMarkup):
            return self.markup == other.markup
        if isinstance(other, basestring):
            return self.markup == other
        return False


class ExpandableHtml(Html):
    '''
        Column type for markup which should be preprocessed on front-end.
        Made in purpose to ensure that source markup is not occasianally outputted on front.
        If it is outputted directly, RuntimeError is raised.
        Use it with corresponding form converter.
    '''

    markup_class = ExpandableMarkup

    def process_bind_param(self, value, dialect):
        if value is not None:
            return unicode(value.markup)



