#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math

from joke.server import db


class Joke(db.Model):
    title = db.TextField()
    content = db.TextField()
    jpg = db.TextField()
    gif = db.TextField()
    origin_id = db.TextField(unique=True)
    origin = db.TextField()
    origin_name = db.TextField()
    origin_uri = db.TextField()
    author_id = db.IntegerField()
    joke_topic = db.TextField()
    comment_count = db.IntegerField()
    create_date = db.DateTimeField()
    is_delete = db.IntegerField()
    
    GET_SQL = ''' SELECT j.*,a.name AS author_name,a.avatar AS author_avatar FROM joke AS j
                  LEFT JOIN author AS a ON j.author_id=a.id;'''
    @db.select()
    def get(self, where=None):
        pass


class Author(db.Model):
    name = db.TextField()
    avatar = db.TextField()
    origin_id = db.TextField(unique=True)
    joke_count = db.IntegerField()
    user_id = db.IntegerField()
    is_delete = db.IntegerField()


class Comment(db.Model):
    content = db.TextField()
    author_id = db.IntegerField()
    create_date = db.DateTimeField()
    is_delete = db.IntegerField()


class Tag(db.Model):
    name = db.TextField()
    create_date = db.DateTimeField()
    is_delete = db.IntegerField()


class JokeTag(db.Model):
    joke_id = db.IntegerField()
    tag_id = db.IntegerField()
    create_time = db.DateTimeField()
    is_delete = db.IntegerField()
