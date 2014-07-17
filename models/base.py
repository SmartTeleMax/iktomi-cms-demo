from iktomi.db.sqla.declarative import AutoTableNameMeta, TableArgsMeta

TABLE_ARGS = {
    'mysql_engine': 'InnoDB',
    'mysql_default charset': 'utf8',
}


class ModelsMeta(AutoTableNameMeta, TableArgsMeta(TABLE_ARGS)):

    pass
