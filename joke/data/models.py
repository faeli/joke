#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math

from joke import db


class Joke(db.Model):
    GET_SQL = ''' SELECT j.*,a.name AS author_name,a.avatar AS author_avatar FROM joke AS j
                  LEFT JOIN author AS a ON j.author_id=a.id;'''
    @db.fair
    def get(self, where=None):
        pass