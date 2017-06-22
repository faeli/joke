#!/usr/bin/env python
# -*- coding: utf-8 -*-
from joke.data.models import Joke
import datetime


def test_select():
    ret = Joke.select({'id':1})
    assert len(ret) == 1
    ret = Joke.select()
    assert len(ret) > 1
    ret = Joke.select(limit=1)
    assert len(ret) == 1
    ret = Joke.select(skip=1,limit=1)
    # print(ret)
    assert ret[0][0] == 2

def test_update():
    ret = Joke.update({'origin':'pengfu'},{'id':1})
    assert ret == 1

# def test_get():
#     model = Joke()
#     assert len(model.get()) == 5

#def test_save():
#    data = {
#        'title': '心有多大，舞台就有多大', 
#        'content': '心有多大',
#        'author_id': 1,
#        'create_date': datetime.datetime.now()
#    }
#    model = Joke(**data)
#    ret = model.get()
#    # print(ret)
#    ret = Joke.insert(**data)
#    print('ret')
#    print(ret)
#    # print(model._meta.fields)
#    # print(model._meta.db_table)
#    assert False
    