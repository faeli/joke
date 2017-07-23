#!/usr/bin/env python
# -*- coding: utf-8 -*-


from sanic import Blueprint
from sanic.response import html
from jinja2 import Environment, PackageLoader
web = Blueprint('web')


from joke.data.models import Joke

print(web.name)


env = Environment(loader=PackageLoader('joke', 'view'))

def view(tpl, **kwargs):
    template = env.get_template(tpl)
    content = template.render(kwargs)
    return html(content)

@web.route('/')
def index(request):
    res = Joke.select(limit=10)
    return view("index.html",title="Ok!",jokes = res)