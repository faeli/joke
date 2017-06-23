#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .db_wrapper import select, insert, update, delete
from .db_url import connect as db_url_connect
from .model import Model
from . import field
from .database import Database


class BaseDb(object):
    def __init__(self, app=None, database=None):
        self.database = None
        self._app = app
        self._db = database
        if app is not None:
            self.init_app(app)
    def __getattr__(self, name):
        cls = type(self)
        # 获取可以使用的数据库类型 Field
        if name.endswith('Field'):
            field = self.database.get_field(name)
            if not field:
                msg = '{.__name__!r} object has no attribute {!r}'
                raise AttributeError(msg.format(cls, name))
            return field
        return super().__getattr__(name)
    
    def _load_database(self, app, config_value):
        if isinstance(config_value, Database):
            database = config_value
        elif isinstance(config_value, dict):
            pass
        else:
            database = db_url_connect(config_value,**app.config['DATABASE_SQL_FILE'])
        
        self.database = database
    
    def init_app(self, app):
        self._app = app
        if self._db is None:
            if 'DATABASE' in app.config:
                initial_db = app.config['DATABASE']
            elif 'DATABASE_URL' in app.config:
                initial_db = app.config['DATABASE_URL']
            else:
                raise ValueError('Missing required configuration data for'
                                 'database: DATABASE or DATABASE_URL.')
        else:
            initial_db = self.db
        
        self.initial_db = initial_db
        self._load_database(app, initial_db)
        return self.initial_db
    
    def get_model_class(self):
        if self.database is None:
            raise RuntimeError('Database must be initialized.')
        
        class BaseModel(Model):
            class Meta:
                database = self.database
        
        return BaseModel    
    
    @property    
    def Model(self):
        if self._app is None:
            database = getattr(self, 'database', None)
            if database is None:
                raise ValueError("Missing database")
        
        if not hasattr(self, '_model_class'):
            self._model_class = self.get_model_class()
        return self._model_class
    
    @property
    def select(self):
        return select
    
    @property
    def insert(self):
        return insert
    
    @property
    def update(self):
        return update
    
    @property
    def delete(self):
        return delete


class SanicDb(BaseDb):
    def __init__(self, app=None, database=None):
        super(SanicDb, self).__init__(app, database)
    
    def init_app(self, app):
        super(SanicDb, self).init_app(app)
        self._register_handlers(app)
    
    def _register_handlers(self, app):
        pass
    

    

        
        