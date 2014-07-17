from functools import partial
from iktomi.unstable.db.sqla.factories import ModelFactories
from iktomi.unstable.utils.functools import return_locals
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship


def model_name(models, name):
    parts = name.split('.')
    model = parts[0] + models.lang.title()
    return '.'.join((model, parts[1])) if len(parts) == 2 else model


def register_m2m_model(source_name, target_name, **kwargs):

    name = kwargs.get('name', source_name + '_' + target_name)
    ordered = kwargs.get('ordered', False)
    source_side = kwargs.get('source_side', None)
    target_side = kwargs.get('target_side', None)
    source = kwargs.get('source_attr', source_name.lower())
    target = kwargs.get('target_attr', target_name.lower())
    source_rel_attrs = kwargs.get('source_rel_attrs', {})
    target_rel_attrs = kwargs.get('target_rel_attrs', {})
    lang = kwargs.get('lang', True)
    langs = kwargs.get('langs', ['ru', 'en'])
    source_id = source + '_id'
    target_id = target + '_id'
    extra = kwargs.get('extra', None)


    def Model(models):
        def _m(name):
            model = models
            for n in name.split('.'):
                model = getattr(models, n)
            return model

        columns = locals()
        columns[source_id] = Column(ForeignKey(
                  _m(source_name).id, ondelete='cascade'),
                  nullable=False, primary_key=True)
        columns[source] = relationship(_m(source_name),
                remote_side=(
                    _m(source_side) if source_side else None),
                foreign_keys=[columns[source_id]],
                **source_rel_attrs)

        columns[target_id] = Column(ForeignKey(
                _m(target_name).id, ondelete='cascade'),
                nullable=False, primary_key=True)

        columns[target] = relationship(_m(target_name),
                remote_side=(
                    _m(target_side) if target_side else None),
                foreign_keys=[columns[target_id]],
                **target_rel_attrs)
        if ordered:
            columns['order_position'] = \
                    Column(Integer, nullable=False, default=0)
        if extra is not None:
            columns.update(return_locals(extra)(models))
        del _m

    Model.__name__ = name
    register_model('BaseModel', lang=lang, langs=langs)(Model)


model_factories = ModelFactories()
register_model = model_factories.register
register_i18n_model = partial(register_model, lang=True)

