#!/usr/bin/env python
# -*- coding: utf-8 -*-
from . import fairdb
from .db_url import connect as db_url_connect
from .model import Model
from .database import Database

class SanicDb(object):
    def __init__(self, app=None, database=None):
        super(SanicDb, self).__init__()
        self.database = None
        self._app = app
        self._db = database
        if app is not None:
            self.init_app(app)
    
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
        
        self._load_database(app, initial_db)
        self._register_handlers(app)
    
    def _load_database(self, app, config_value):
        if isinstance(config_value, Database):
            database = config_value
        elif isinstance(config_value, dict):
            pass
        else:
            database = db_url_connect(config_value,**app.config['DATABASE_SQL_FILE'])
        
        self.database = database

    def _register_handlers(self, app):
        pass
    
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
    def fair(self):
        return fairdb