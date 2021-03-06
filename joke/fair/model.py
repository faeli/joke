#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from copy import deepcopy
from bisect import bisect_left
from bisect import bisect_right
from . import logger
from .field import *
from .result import DictQueryResultWrapper
# Python 2/3 compatibility helpers. These helpers are used internally and are
# not exported.
_METACLASS_ = '_metaclass_helper_'
def with_metaclass(meta, base=object):
    return meta(_METACLASS_, (base,), {})


class CompositeKey(object):
    pass


class _SortedFieldList(object):
    __slots__ = ('_keys', '_items')

    def __init__(self):
        self._keys = []
        self._items = []

    def __getitem__(self, i):
        return self._items[i]

    def __iter__(self):
        return iter(self._items)

    def __contains__(self, item):
        k = item._sort_key
        i = bisect_left(self._keys, k)
        j = bisect_right(self._keys, k)
        return item in self._items[i:j]

    def index(self, field):
        return self._keys.index(field._sort_key)

    def insert(self, item):
        k = item._sort_key
        i = bisect_left(self._keys, k)
        self._keys.insert(i, k)
        self._items.insert(i, item)

    def remove(self, item):
        idx = self.index(item)
        del self._items[idx]
        del self._keys[idx]


class ModelOptions(object):
    def __init__(self, cls, database=None, db_table=None, db_table_func=None,
                 indexes=None, order_by=None, primary_key=None,
                 table_alias=None, constraints=None, schema=None,
                 validate_backrefs=True, only_save_dirty=False,
                 depends_on=None, **kwargs):
        self.model_class = cls
        self.name = cls.__name__.lower()
        self.fields = {}
        self.columns = {}
        self.defaults = {}
        self._default_by_name = {}
        self._default_dict = {}
        self._default_callables = {}
        self._default_callable_list = []
        self._sorted_field_list = _SortedFieldList()
        self.sorted_fields = []
        self.sorted_field_names = []
        self.valid_fields = set()
        self.declared_fields = []

        self.database = database if database is not None else default_database
        self.db_table = db_table
        self.db_table_func = db_table_func
        self.indexes = list(indexes or [])
        self.order_by = order_by
        self.primary_key = primary_key
        self.table_alias = table_alias
        self.constraints = constraints
        self.schema = schema
        self.validate_backrefs = validate_backrefs
        self.only_save_dirty = only_save_dirty
        self.depends_on = depends_on

        self.auto_increment = None
        self.composite_key = False
        self.rel = {}
        self.reverse_rel = {}

        for key, value in kwargs.items():
            setattr(self, key, value)
        self._additional_keys = set(kwargs.keys())

        if self.db_table_func and not self.db_table:
            self.db_table = self.db_table_func(cls)

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.name)

    def prepared(self):
        if self.order_by:
            norm_order_by = []
            for item in self.order_by:
                if isinstance(item, Field):
                    prefix = '-' if item._ordering == 'DESC' else ''
                    item = prefix + item.name
                field = self.fields[item.lstrip('-')]
                if item.startswith('-'):
                    norm_order_by.append(field.desc())
                else:
                    norm_order_by.append(field.asc())
            self.order_by = norm_order_by

    def _update_field_lists(self):
        self.sorted_fields = list(self._sorted_field_list)
        self.sorted_field_names = [f.name for f in self.sorted_fields]
        self.valid_fields = (set(self.fields.keys()) |
                             set(self.fields.values()) |
                             set((self.primary_key,)))
        self.declared_fields = [field for field in self.sorted_fields
                                if not field.undeclared]

    def add_field(self, field):
        self.remove_field(field.name)
        self.fields[field.name] = field
        self.columns[field.db_column] = field

        self._sorted_field_list.insert(field)
        self._update_field_lists()

        if field.default is not None:
            self.defaults[field] = field.default
            if callable(field.default):
                self._default_callables[field] = field.default
                self._default_callable_list.append((field.name, field.default))
            else:
                self._default_dict[field] = field.default
                self._default_by_name[field.name] = field.default

    def remove_field(self, field_name):
        if field_name not in self.fields:
            return
        original = self.fields.pop(field_name)
        del self.columns[original.db_column]
        self._sorted_field_list.remove(original)
        self._update_field_lists()

        if original.default is not None:
            del self.defaults[original]
            if self._default_callables.pop(original, None):
                for i, (name, _) in enumerate(self._default_callable_list):
                    if name == field_name:
                        self._default_callable_list.pop(i)
                        break
            else:
                self._default_dict.pop(original, None)
                self._default_by_name.pop(original.name, None)

    def get_default_dict(self):
        dd = self._default_by_name.copy()
        for field_name, default in self._default_callable_list:
            dd[field_name] = default()
        return dd

    def get_field_index(self, field):
        try:
            return self._sorted_field_list.index(field)
        except ValueError:
            return -1

    def get_primary_key_fields(self):
        if self.composite_key:
            return [
                self.fields[field_name]
                for field_name in self.primary_key.field_names]
        return [self.primary_key]

    def rel_for_model(self, model, field_obj=None, multi=False):
        is_field = isinstance(field_obj, Field)
        is_node = not is_field and isinstance(field_obj, Node)
        if multi:
            accum = []
        for field in self.sorted_fields:
            if isinstance(field, ForeignKeyField) and field.rel_model == model:
                is_match = (
                    (field_obj is None) or
                    (is_field and field_obj.name == field.name) or
                    (is_node and field_obj._alias == field.name))
                if is_match:
                    if not multi:
                        return field
                    accum.append(field)
        if multi:
            return accum

    def reverse_rel_for_model(self, model, field_obj=None, multi=False):
        return model._meta.rel_for_model(self.model_class, field_obj, multi)

    def rel_exists(self, model):
        return self.rel_for_model(model) or self.reverse_rel_for_model(model)

    def related_models(self, backrefs=False):
        models = []
        stack = [self.model_class]
        while stack:
            model = stack.pop()
            if model in models:
                continue
            models.append(model)
            for fk in model._meta.rel.values():
                stack.append(fk.rel_model)
            if backrefs:
                for fk in model._meta.reverse_rel.values():
                    stack.append(fk.model_class)
        return models


class BaseModel(type):
    inheritable = set([
        'constraints', 'database', 'db_table_func', 'indexes', 'order_by',
        'primary_key', 'schema', 'validate_backrefs', 'only_save_dirty'])

    def __new__(cls, name, bases, attrs):
        if name == _METACLASS_ or bases[0].__name__ == _METACLASS_:
            return super(BaseModel, cls).__new__(cls, name, bases, attrs)

        meta_options = {}
        meta = attrs.pop('Meta', None)
        if meta:
            for k, v in meta.__dict__.items():
                if not k.startswith('_'):
                    meta_options[k] = v

        model_pk = getattr(meta, 'primary_key', None)
        parent_pk = None

        # inherit any field descriptors by deep copying the underlying field
        # into the attrs of the new model, additionally see if the bases define
        # inheritable model options and swipe them
        for b in bases:
            if not hasattr(b, '_meta'):
                continue

            base_meta = getattr(b, '_meta')
            if parent_pk is None:
                parent_pk = deepcopy(base_meta.primary_key)
            all_inheritable = cls.inheritable | base_meta._additional_keys
            for (k, v) in base_meta.__dict__.items():
                if k in all_inheritable and k not in meta_options:
                    meta_options[k] = v

            for (k, v) in b.__dict__.items():
                if k in attrs:
                    continue
                if isinstance(v, FieldDescriptor):
                    if not v.field.primary_key:
                        attrs[k] = deepcopy(v.field)

        # initialize the new class and set the magic attributes
        cls = super(BaseModel, cls).__new__(cls, name, bases, attrs)
        ModelOptionsBase = meta_options.get('model_options_base', ModelOptions)
        cls._meta = ModelOptionsBase(cls, **meta_options)
        cls._data = None
        cls._meta.indexes = list(cls._meta.indexes)

        if not cls._meta.db_table:
            cls._meta.db_table = re.sub('[^\w]+', '_', cls.__name__.lower())

        # replace fields with field descriptors, calling the add_to_class hook
        fields = []
        for name, attr in cls.__dict__.items():
            if isinstance(attr, Field):
                if attr.primary_key and model_pk:
                    raise ValueError('primary key is overdetermined.')
                elif attr.primary_key:
                    model_pk, pk_name = attr, name
                else:
                    fields.append((attr, name))

        composite_key = False
        if model_pk is None:
            if parent_pk:
                model_pk, pk_name = parent_pk, parent_pk.name
            else:
                model_pk, pk_name = PrimaryKeyField(primary_key=True), 'id'
        if isinstance(model_pk, CompositeKey):
            pk_name = '_composite_key'
            composite_key = True

        if model_pk is not False:
            model_pk.add_to_class(cls, pk_name)
            cls._meta.primary_key = model_pk
            cls._meta.auto_increment = (
                isinstance(model_pk, PrimaryKeyField) or
                bool(model_pk.sequence))
            cls._meta.composite_key = composite_key

        # 添加 filed 到 cls 上，并调用 ModelOptions.add_field
        for field, name in fields:
            field.add_to_class(cls, name)

        # create a repr and error class before finalizing
        if hasattr(cls, '__unicode__'):
            setattr(cls, '__repr__', lambda self: '<%s: %r>' % (
                cls.__name__, self.__unicode__()))

        # exc_name = '%sDoesNotExist' % cls.__name__
        # exc_attrs = {'__module__': cls.__module__}
        # exception_class = type(exc_name, (DoesNotExist,), exc_attrs)
        # cls.DoesNotExist = exception_class
        # cls._meta.prepared()
        #
        # if hasattr(cls, 'validate_model'):
        #     cls.validate_model()
        #
        # DeferredRelation.resolve(cls)

        return cls

    def __iter__(self):
        return iter(self.select())



class Model(with_metaclass(BaseModel)):
    INSERT_SQL = '''INSERT INTO {db_table}({columns}) VALUES({values});'''
    SELECT_SQL = '''SELECT {columns} FROM {db_table}'''
    UPDATE_SQL = '''UPDATE {db_table} SET {sets} WHERE {wheres};'''
    def __init__(self, *args, **kwargs):
        self._data = self._meta.get_default_dict()
        self._dirty = set(self._data)
        self._obj_cache = {}
        
        # print(self._data)
        
        for k, v in kwargs.items():
            setattr(self, k, v)
    
    @classmethod
    def insert(cls, __data=None, **insert):
        fdict = __data or {}
        fdict.update([(cls._meta.fields[f], insert[f]) for f in insert])
        columns = []
        values = []
        values_placeholder = []
        for key, value in fdict.items():
            if isinstance(key, Field):
                print('%s = %s' %(key.name, value))
                columns.append(key.name)
                values.append(value)
                values_placeholder.append('?')
            elif isinstance(key, str):
                print('%s = %s' %(key, value))
        
        sql = cls.INSERT_SQL.format(db_table=cls._meta.db_table, columns=",".join(columns), values=",".join(values_placeholder))
        cursor = cls._meta.database.execute_sql(sql, values)
        return cls._meta.database.last_insert_id(cursor, cls)
    
    @classmethod
    def select(cls, where=None, limit=-1, skip=-1, columns=None):
        sql = cls.SELECT_SQL
        wheres = []
        if columns is None:
            columns = list(cls._meta.columns.keys())
        params =[]
        formats = {
            'db_table': cls._meta.db_table, 
            'columns': ",".join(columns)
        }
        if where:
            sql += ''' WHERE {wheres}'''
            for key, value in where.items():
                wheres.append('%s=?' %(key))
                params.append(value)
            formats['wheres'] = " AND ".join(wheres)
        sql = sql.format(**formats)
        
        limit_str = ''' LIMIT {skip},{limit}'''
        if skip > 0:
            limit_str = limit_str.format(skip=skip, limit=limit or 1)
        elif limit > 0:
            limit_str = limit_str.format(skip=skip or 0, limit=limit)
        
        if skip > 0 or limit > 0:
            sql += limit_str
        cursor = cls._meta.database.execute_sql(sql, params)
        # TODO Objeck
        result = cls._query_result_wrapper(cursor)
        return result
    
    @classmethod
    def update(cls, update=None, where=None):
        if not where:
            raise RuntimeError("must where")
        if not update:
            raise RunttimeError("must update")
        formats = {
            'db_table': cls._meta.db_table
        }
        sets = []
        params = []
        for key, value in update.items():
            sets.append('%s=?' % key)
            params.append(value)
        wheres = []
        for key, value in where.items():
            wheres.append('%s=?' % key)
            params.append(value)
        formats['sets'] = ",".join(sets)
        formats['wheres'] = " AND ".join(wheres)
        sql = cls.UPDATE_SQL.format(**formats)
        cursor = cls._meta.database.execute_sql(sql, params)
        return cursor.rowcount
    
    @classmethod
    def _query_result_wrapper(cls, cursor):
        # TODO 处理查询返回数据
        return DictQueryResultWrapper(cls, cursor)
    
    def save(self, where=None):
        field_dict = dict(self._data)
        # 先按主键/unique键值查询，查询不到=新增，查询到=修改
        old_doc = None
        if where is not None:
            rets = [i for i in self.select(where,1)]
            if len(rets) == 1:
                old_doc = rets[0]
            print(old_doc)
        if old_doc is not None:
            self.id = old_doc['id']
            return self.update(field_dict, where)
        else:
            last_insert_id = self.insert(**field_dict)
            self.id = last_insert_id
            return last_insert_id
    
    def exec_sql(self, sql, params):
        # sql = sql.format(**params)
        cursor = self._meta.database.execute_sql(sql,params)
        # TODO test
        # for i in dir(cursor):
        #     if not i.startswith('__'):
        #         print(i)
        #         # print(cursor[i])
        # for i in cursor.description:
        #     print(i)
        return cursor
    
    def compile_sql(self, sql, kwargs):
        # TODO 根据 sql 分析出查询出的字段，并取出需要的参数
        sql = sql.format(**kwargs)
        return sql
    
    def func_exec(self, sql, options, **kwargs):
        logger.info(sql)
        ret = None
        sql_type = 'SELECT'
        if 'ret' in options:
            ret = options['ret']
        
        if 'sql_type' in options:
            sql_type = options['sql_type']
        
        # sql = sql.format(**kwargs)
        for k, v in kwargs.items():
            print('%s = %s' % (k, v))
        sql = self.compile_sql(sql, kwargs)
        cursor = self.exec_sql(sql, kwargs)
        data = None
        
        if sql_type =='SELECT':
            result = self._query_result_wrapper(cursor)
            data = []
            for item in result:
                data.append(item)
        elif sql_type == 'UPDATE':
            data = cursor.rowcount
        elif sql_type == 'DELETE':
            data = cursor.rowcount
        elif sql_type == 'INSERT':
            data = self._meta.database.last_insert_id(cursor, self) or cursor.rowcount
        return data
    