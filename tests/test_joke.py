#!/usr/bin/env python
# -*- coding: utf-8 -*-
from joke.data.models import Joke


def test_models_joke_get():
    model = Joke()
    assert len(model.get().fetchall()) == 0
