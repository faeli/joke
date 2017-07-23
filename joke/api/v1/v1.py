#!/usr/bin/env python
# -*- coding: utf-8 -*-


from sanic import Blueprint
from sanic.response import json

from joke.data.models import Joke

v1 = Blueprint('v1', url_prefix='/v1')

@v1.route("/joke")
def joke(request):
    res = Joke.select(limit=10)
    return json(res)