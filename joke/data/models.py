#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math

from .sqlite import DbSQLite


class SQLiteModel(DbSQLite):
    INSERT_SQL = ''' INSERT INTO {table_name}({fields})
                     VALUES({values});'''
    SELECT_SQL = ''' SELECT {fields} FROM {table_name}'''
    def __init__(self):
        super(SQLiteModel, self).__init__()
    
    def get_table_name(self):
        table_name = self.__class__.__name__.lower()
        if '_table_name' in self.__class__.__dict__:
            table_name = self.__class__.__dict__['_table_name']
        return table_name
    
    def insert(self, kv=None):
        table_name = self.get_table_name()
        fields = []
        values = []
        
        if kv:
            if type(kv) == dict:
                fields = list(kv.keys())
                values = list(kv.values())
        else:
            pass
        
        placeholder = []
        for i in values:
            placeholder.append('?')

        sql = self.INSERT_SQL.format(table_name=table_name,fields=",".join(fields),values=",".join(placeholder))
        print(sql)
    
    def save(self, kv=None):
        self.insert(kv)
    
    @staticmethod    
    def db(func):
        def inner(*args, **kwargs):
            return func(args,kwargs)
        return inner
    
class Joke(SQLiteModel):
    _table_name = 'joke'
    
    GET_SQL = ''' SELECT j.*,a.name AS author_name,a.avatar AS author_avatar FROM joke AS j
                  LEFT JOIN author AS a ON j.author_id=a.id;'''
    
    def db(func):
        def inner(*args, **kwargs):
            self = args[0]
           
            sql_name = '_'.join([func.__name__,'sql']).upper()
            print(self.__class__.__dict__[sql_name])
            return func(args,kwargs)
        return inner
    
    @db
    def get(self, where=None):
        pass