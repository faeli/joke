#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from .pengfu import Pengfu
from .file import DownloadImage
from progress.counter import Counter


from joke import celery, app
from joke.data.models import Author, Joke


APP_DIR = app.config['APP_DIR']

pengfu = Pengfu()
jokeImg = DownloadImage({'res':'res/images/joke'})
avatarImg = DownloadImage({'res':'res/images/avatar'})
def saveJoke(joke):
    if 'jpg' in joke and joke['jpg']:
        joke['jpg'] = jokeImg.load(joke['jpg'])
    if 'gif' in joke and joke['gif']:
        joke['gif'] = jokeImg.load(joke['gif'])
    if 'author_avatar' in joke and joke['author_avatar']:
        joke['author_avatar'] = avatarImg.load(joke['author_avatar'])
    
    author = {
        'name': joke.pop('author_name'),
        'avatar': joke.pop('author_avatar'),
        'origin_id': joke.pop('author_id')
    }
    comments = joke.pop('comments', None)
    tags = joke.pop('tags', None)
    # author
    author['user_id'] = 1
    am = Author(**author)
    author_id = am.save(where={'origin_id': author.get('origin_id')})
    # joke
    joke['author_id'] = am.id
    joke['create_date'] = datetime.datetime.now()
    jm = Joke(**joke)
    jm.save(where={'origin_id': joke.get('origin_id')})
    joke_id = jm.id
    # tags
    if tags is not None:
        pass
    # comments
    if comments is not None:
        pass
    
    return True

@celery.task(name="sync_joke_pengfu_task")
def sync_joke_pengfu_task(index=None):
    pf_counter = Counter("Pengfu Count:")
    def save(jokes):
        for joke in jokes:
            saveJoke(joke)
            pf_counter.next()
    return pengfu.sync(save=save,index=index)