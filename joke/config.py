#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os

RES_URI = 'res'
STATIC_URI = 'res/static'
IMAGES_URI = 'res/images'

class Config(object):
    """"""
    APP_DIR = os.path.dirname(os.path.realpath(__file__))
    
    # env 
    ENV = "DEV"
    
    # DB file
    DB_FILE = 'joke-%s.db' % ENV
    
    # DB sql file
    DATABASE_SQL_FILE = {
        'init_file': '%s/data/init-db.sql' % APP_DIR,
        'upgrade_file': '%s/data/upgrade-db.sql' % APP_DIR
    }
    
    # SQLite file
    DATABASE = 'sqlite:///%s' % os.path.join(APP_DIR, DB_FILE)
    
    # CELERY config
    CELERY = {}

class ProdConfig(Config):
    """Production"""
    ENV = 'PROD'

class DevConfig(Config):
    """Developer"""
    
def load_config():
    import os
    mode = os.environ.get('JOKE_ENV','DEV').upper()
    
    if mode == 'PROD':
        return ProdConfig
    else:
        return DevConfig