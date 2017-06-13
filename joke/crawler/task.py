#!/usr/bin/env python
# -*- coding: utf-8 -*-


from .pengfu import Pengfu
from .file import DownloadImage
from progress.counter import Counter

from joke import celery

pengfu = Pengfu()
jokeImg = DownloadImage({'res':'joke/res/images/joke'})
avatarImg = DownloadImage({'res':'joke/res/images/avatar'})
def saveJoke(joke):
    print(joke)
    if 'jpg' in joke and joke['jpg']:
        jokeImg.load(joke['jpg'])
    if 'gif' in joke and joke['gif']:
        jokeImg.load(joke['gif'])
    if 'author_avatar' in joke and joke['author_avatar']:
        avatarImg.load(joke['author_avatar'])
    # downloadFile

@celery.task(name="sync_joke_pengfu_task")
def sync_joke_pengfu_task(index=None):
    pf_counter = Counter("Pengfu Count:")
    def save(jokes):
        for joke in jokes:
            saveJoke(joke)
            pf_counter.next()
    return pengfu.sync(save=save,index=index)