#!/usr/bin/env python
# -*- coding: utf-8 -*-
import inspect
from . import logger


def select(**options):
    def wrapper(func):
        def generator(*args, **kwargs):
            return _wrapper('SELECT', func, options, args, kwargs)
        return generator
    return wrapper


def update(**options):
    def wrapper(func):
        def generator(*args, **kwargs):
            return _wrapper('UPDATE', func, options, args, kwargs)
        return generator
    return wrapper
    

def delete(**options):
    def wrapper(func):
        def generator(*args, **kwargs):
            return _wrapper('DELETE', func, options, args, kwargs)
        return generator
    return wrapper

def insert(**options):
    def wrapper(func):
        def generator(*args, **kwargs):
            return _wrapper('INSERT', func, options, args, kwargs)
        return generator
    return wrapper

def _wrapper(sql_type, func, options, args, kwargs):
    if not options:
        options = {}
    options['sql_type'] = sql_type
    fargs, varargname, kwname = inspect.getargspec(func)[:3]
    dictArgs = _getcallargs(fargs, varargname, kwname, args, kwargs)
    self = dictArgs.pop('self')
    sql_name = '_'.join([func.__name__,'sql']).upper()
    sql = self.__class__.__dict__[sql_name]
    return self.__class__.func_exec(self, sql, options, **dictArgs)

def _getcallargs(args, varargname, kwname, varargs, keywords):
    dctArgs = {}
    varargs = tuple(varargs)
    keywords = dict(keywords)
     
    argcount = len(args)
    varcount = len(varargs)
    callvarargs = None
     
    if argcount <= varcount:
        for n, argname in enumerate(args):
            dctArgs[argname] = varargs[n]
         
        callvarargs = varargs[-(varcount-argcount):]
     
    else:
        for n, var in enumerate(varargs):
            dctArgs[args[n]] = var
         
        for argname in args[-(argcount-varcount):]:
            if argname in keywords:
                dctArgs[argname] = keywords.pop(argname)
         
        callvarargs = ()
     
    if varargname is not None:
        dctArgs[varargname] = callvarargs
     
    if kwname is not None:
        dctArgs[kwname] = keywords
     
    dctArgs.update(keywords)
    return dctArgs
