#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Joke"""

import asyncio
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

from sanic import Sanic
from joke.config import load_config
from joke.fair.ext import SanicDb
# config
CONFIG = load_config()

# Sanic App
app = Sanic(__name__)
app.config.from_object(CONFIG)

# Db
#from joke.data import SQLiteData
db = SanicDb(app)

# io loop
loop = asyncio.get_event_loop()

# Celery Task
def make_celery(app):
    from celery import Celery, platforms
    platforms.C_FORCE_ROOT = True
    name = "".join([app.name, '_', app.config['ENV']])
    celery_instance = Celery(name,**app.config['CELERY'])
    celery_instance.conf.update(app.config['CELERY'])
    
    return celery_instance

celery = make_celery(app)

# Static File

app.static('/favicon.ico','./res/favicon.png')
app.static('/res','./res')

# blueprint api v1
from joke.api import v1
app.blueprint(v1)
# blueprint web view
from joke.view import web
app.blueprint(web)