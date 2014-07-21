# -*- coding: utf-8 -*-

def url_for_object(env, obj):
    ''' Get url for given object on front site.
        MUST return reverse object.
    '''
    reverse = env.lang.root
    models = env.models

    if isinstance(obj, models.Doc):
        return reverse.events.item(id=obj.id)
    if isinstance(obj, models.Section):
        return reverse.by_section(section_slug=obj.slug)
    obj_id = getattr(obj, 'id', '')
    raise ValueError(u'Unable to find reverse for an object {} {}'
                         .format(repr(obj), obj_id))
