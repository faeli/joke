#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import inspect


try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self,record):
            pass


logger = logging.getLogger('fair')
logger.addHandler(NullHandler())


def fairdb(func):
    def generator(*args, **kwargs):
        fargs, varargname, kwname = inspect.getargspec(func)[:3]
        dictArgs = _getcallargs(fargs, varargname, kwname, args, kwargs)
        self = dictArgs.pop('self')
        sql_name = '_'.join([func.__name__,'sql']).upper()
        sql = self.__class__.__dict__[sql_name]
        return self.__class__.func_exec(self, sql, **dictArgs)
    
    return generator

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
