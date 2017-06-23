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
