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
    ret = Joke.select(skip=1, limit=1)
    assert len(ret) == 1
    for i in ret:
        print(i)
    ret = Joke.select()
    assert len(ret) > 0

def test_update():
    ret = Joke.update({'origin':'pengfu'},{'id':4})
    assert ret == 1

def test_get():
    model = Joke()
    ret = model.get()
    print(ret)
    assert len(model.get()) > 1

def test_save():
   data = {
       'title': '心有多大，舞台就有多大',
       'content': '心有多大',
       'author_id': 1,
       'origin_id': 'test_1',
       'create_date': datetime.datetime.now()
   }
   model = Joke(**data)
   ret = model.save(where={'origin_id':'test_1'})
   assert model.id > 0
   
   model2 = Joke(**data)
   model2.content = '心有多大，舞台就有多大'
   ret = model2.save(where={'id': model.id})
   assert model.id == model2.id