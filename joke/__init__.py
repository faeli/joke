#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Joke"""
from joke.server import app, loop, celery
__ALL__ = ('app', 'loop', 'celery')