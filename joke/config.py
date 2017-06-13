#!/usr/bin/env python
# -*- coding: utf-8 -*-


RES_URI = 'res'
STATIC_URI = 'res/static'
IMAGES_URI = 'res/images'

class Config(object):
    """"""
    # env 
    ENV = "DEV"
    
    # SQLite file
    DB_FILE = 'joke.db'
    
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