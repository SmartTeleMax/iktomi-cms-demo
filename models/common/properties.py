# -*- coding: utf-8 -*-

from weakref import WeakKeyDictionary
from models.common.fields import Column
from sqlalchemy.orm import ColumnProperty
from sqlalchemy import select, func, text, event
from iktomi.unstable.utils.image_resizers import Resizer


class FilteredProperty(object):

    def __init__(self, prop_name, **filters):
        self.prop_name = prop_name
        self.filters = filters
        self._cache = WeakKeyDictionary()

    def __get__(self, inst, cls):
        if inst is None:
            return self
        if not inst in self._cache:
            self._cache[inst] = result = []
            for item in getattr(inst, self.prop_name):
                if not item:
                    # This is a trick to filter out unpublished items on front.
                    # Just define proper __nonzero__ method.
                    continue
                for name, value in self.filters.items():
                    if getattr(item, name) != value:
                        break
                else:
                    result.append(item)
        return self._cache[inst]

    def __set__(self, inst, items):
        self._cache[inst] = items
        for index, item in enumerate(items):
            for name, value in self.filters.items():
                setattr(item, name, value)
        result = []
        for item in getattr(inst, self.prop_name):
            for name, value in self.filters.items():
                if getattr(item, name) != value:
                    result.append(item)
                    break
        result.extend(items)
        setattr(inst, self.prop_name, result)


def OrderColumn(*a, **kw):
    return OrderColumnProperty(Column(*a, **kw))


class OrderColumnProperty(ColumnProperty):
    def before_insert(self, mapper, conn, target):
        column = self.columns[0]
        if getattr(target, column.name) is None:
            order = conn.execute(select([func.max(column) + text('1')])).scalar()
            setattr(target, column.name, order)

    def instrument_class(self, mapper):
        ColumnProperty.instrument_class(self, mapper)
        event.listen(mapper, 'before_insert', self.before_insert)


class ResizeCropUpper(Resizer):
    def transformations(self, size, target_size):
        sw, sh = size
        tw, th = target_size
        if not self.expand and sw<=tw and sh<=th:
            return []
        transforms = []
        if sw*th>sh*tw:
            if sh!=th and (sh>th or self.expand):
                w = sw*th//sh
                transforms.append(('resize', (w, th)))
                sw, sh = w, th
            if sw>tw:
                wd = (sw-tw)//2
                transforms.append(('crop', (wd, 0, tw+wd, sh)))
        else:
            if sw!=tw and (sw>tw or self.expand):
                h = sh*tw//sw
                transforms.append(('resize', (tw, h)))
                sw, sh = tw, h
            if sh>th:
                d = sh-th
                upper_cut = d // 3
                transforms.append(('crop', (0, upper_cut, sw, th+upper_cut)))
        return transforms
