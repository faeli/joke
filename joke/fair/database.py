#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
from . import logger


class _BaseConnectionLocal(object):
    def __init__(self, **kwargs):
        super(_BaseConnectionLocal, self).__init__(**kwargs)
        self.autocommit = None
        self.closed = True
        self.conn = None
        self.context_stack = []
        self.transactions = []


class _ConnectionLocal(_BaseConnectionLocal, threading.local):
    pass


class Database(object):
    def __init__(self, database,  threadlocals=True, autocommit=True, **connect_kwargs):
        self.connect_kwargs = {}
        if threadlocals:
            self._local = _ConnectionLocal()
        else:
            self._local = _BaseConnectionLocal()
        self.init(database, **connect_kwargs)
        
        self._conn_lock = threading.Lock()
        self.autocommit = autocommit
        
    def init(self, database, **connect_kwargs):
        self.deferred = database is None
        self.database = database
        if 'init_file' in connect_kwargs:
            self.init_file = connect_kwargs.pop('init_file')
        if 'upgrade_file' in connect_kwargs:
            self.upgrade_file = connect_kwargs.pop('upgrade_file')
        self.connect_kwargs.update(connect_kwargs)
    
    def connect(self):
        with self._conn_lock:
            self._local.conn = self._create_connection()
            self._local.closed = False
    
    def get_conn(self):
        if self._local.context_stack:
            conn = self._local.context_stack[-1].connection
            if conn is not None:
                return conn
        if self._local.closed:
            self.connect()
        return self._local.conn
    
    def close(self):
        with self._conn_lock:
            self._close(self._local.conn)
            self._local.closed = True
    
    def is_closed(self):
        return self._local.closed
    
    def get_cursor(self):
        return self.get_conn().cursor()
    
    def commit(self):
        self.get_conn().commit()
    
    def rollback(self):
        self.get_conn().rollback()
    
    def set_autocommit(self, autocommit):
        self._local.autocommit = autocommit
    
    def get_autocommit(self):
        if self._local.autocommit is None:
            self.set_autocommit(self.autocommit)
        return self._local.autocommit
    
    def execute_sql(self, sql, params=None, require_commit=True):
        logger.debug(sql, params)
        cursor = self.get_cursor()
        try:
            cursor.execute(sql, params or ())
        except Exception:
            if self.autorollback and self.get_autocommit():
                self.rollback()
            raise
        else:
            if require_commit and self.get_autocommit():
                self.commit()
        return cursor
    
    def _create_connection(self):
        return self._connect(self.database, **self.connect_kwargs)
    
    def _connect(self, database, **kwargs):
        raise NotImplementedError
    
    def _close(self, conn):
        conn.close()


# SQLite3 database

try:
    from pysqlite2 import dbapi2 as pysq3
except ImportError:
    pysq3 = None
try:
    import sqlite3
except ImportError:
    sqlite3 = pysq3
else:
    if pysq3 and pysq3.sqlite_version_info >= sqlite3.sqlite_version_info:
        sqlite3 = pysq3

class SQLiteDatabase(Database):
    def __init__(self, database, _pragmas=None, *args, **kwargs):
        self.init_file = None
        self.upgrade_file = None
        self._pragmas = _pragmas or []
        journal_mode = kwargs.pop('journal_mode', None)
        if journal_mode:
            self._pragmas.append(('journal_mode', journal_mode))
        
        super(SQLiteDatabase, self).__init__(database,*args,**kwargs)
    
    def _connect(self, database, **kwargs):
        if not sqlite3:
            raise RuntimeError('pysqlite or sqlite3 must be installed.')
        conn = sqlite3.connect(database,**kwargs)
        conn.isolation_level = None
        try:
            self._add_conn_hooks(conn)
        except:
            conn.close()
            raise
        return conn
    
    def _add_conn_hooks(self, conn):
        self._set_pragmas(conn)
        self._init_db(conn)
        self._upgrade_db(conn)
    
    def _set_pragmas(self, conn):
        if self._pragmas:
            cursor = conn.cursor()
            for pragma, value in self._pragmas:
                cursor.execute('PRAGMA %s=%s;' % (pragma, value))
            cursor.close()
    def _init_db(self, conn):
        if self.init_file and self.init_file:
            cur = conn.cursor()
            init_file = open(self.init_file)
            try:
                init_sql = " ".join(init_file.readlines())
                cur.executescript(init_sql);
            finally:
                init_file.close()
                cur.close()
    
    def _upgrade_db(self, conn):
        if self.upgrade_file:
            cur = conn.cursor()
            upgrade_file = open(self.upgrade_file)
            try:
                upgrade_sql = " ".join(upgrade_file.readlines())
                cur.executescript(upgrade_sql)
            finally:
                upgrade_file.close()
                cur.close()
    
    def pragma(self, key, value=None):
        sql = 'PRAGMA $s' % key
        if value:
            sql += ' = %s' % value
        return self.execute_sql(sql).fetchone()