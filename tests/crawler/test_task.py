#!/usr/bin/env python
# -*- coding: utf-8 -*-

from joke.crawler.task import sync_joke_pengfu_task


def test_sync_joke_pengfu_task():
    sync_joke_pengfu_task(index=1)
    
    assert False