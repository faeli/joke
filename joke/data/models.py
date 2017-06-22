#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math

from joke import db


class Joke(db.Model):
    title = db.TextField()
    content = db.TextField()
    jpg = db.TextField()
    gif = db.TextField()
    origin_id = db.TextField()
    origin = db.TextField()
    origin_uri = db.TextField()
    author_id = db.IntegerField()
    joke_topic = db.TextField()
    comment_count = db.IntegerField()
    create_date = db.DataTimeField()
    is_delete = db.IntegerField()
    
    GET_SQL = ''' SELECT j.*,a.name AS author_name,a.avatar AS author_avatar FROM joke AS j
                  LEFT JOIN author AS a ON j.author_id=a.id;'''
    @db.fair(ret=list)
    def get(self, where=None):
        pass