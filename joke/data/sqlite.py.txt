#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sqlite3


class DbSQLite(object):
    def __init__(self, db_file=None):
        if not db_file:
            from joke import app
            db_file = app.config['DB_FILE']
        self.db_file = db_file
        real_path = os.path.dirname(os.path.realpath(__file__))
        self.init_file = os.sep.join([real_path,'init-db.sql'])
        self.upgrade_file = os.sep.join([real_path,'upgrade-db.sql'])
        self.init()
    
    def init(self):
        db = self.get_db()
        cur = db.cursor()
        init_file = open(self.init_file)
        try:
            init_sql = " ".join(init_file.readlines())
            cur.executescript(init_sql);
        finally:
            init_file.close()
        upgrade_file = open(self.upgrade_file)
        try:
            upgrade_sql = " ".join(upgrade_file.readlines())
            cur.executescript(upgrade_sql)
        finally:
            upgrade_file.close()
        cur.close()
        db.close()
    
    def get_db(self, db_file=None):
        if not db_file:
            db_file = self.db_file
        return sqlite3.connect(db_file)
    
    def execute(self, sql, params=None):
        db = self.get_db()
        try:
            cur = db.cursor()
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
            cur.close()
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()