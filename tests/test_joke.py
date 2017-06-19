#!/usr/bin/env python
# -*- coding: utf-8 -*-
from joke import db

class JokeModel(db.Model):
    TEST_SQL = '''SELECT {a}+{b};'''
    @db.fair
    def test(self, a, b):
        pass

def test_db():
    model = JokeModel()
    assert model.test(2, 4).fetchone()[0] == 6
