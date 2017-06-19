#!/usr/bin/env python
# -*- coding: utf-8 -*-
from joke.data.models import Joke


def test_get():
    model = Joke()
    assert len(model.get().fetchall()) == 0

def test_save():
    model = Joke(title='心有多大，舞台就有多大', content='心有多大')
    print(model)
    assert False
    