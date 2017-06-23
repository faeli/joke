#!/usr/bin/env python
# -*- coding: utf-8 -*-

class ResultIterator(object):
    def __init__(self, qrw):
        self.qrw = qrw
        self._idx = 0
        
    def __next__(self):
        if self._idx < self.qrw._ct:
            obj = self.qrw._result_cache[self._idx]
        elif not self.qrw._populated:
            obj = self.qrw.iterate()
            self.qrw._result_cache.append(obj)
            self.qrw._ct +=1
        else:
            raise StopIteration
        self._idx += 1
        return obj

class QueryResultWrapper(object):
    def __init__(self, model, cursor, meta=None):
        self.model = model
        self.cursor = cursor
        self.column_names = []
        self.row_size = 0
        self._ct = self._idx = 0
        self._populated = self._initialized = False
        self._result_cache = []
    
    def __iter__(self):
        if self._populated:
            return iter(self._result_cache)
        return ResultIterator(self)
    def __next__(self):
        if self._idx < self._ct:
            inst = self._result_cache[self._idx]
            self._idx += 1
            return inst
        elif self._populated:
            raise StopIteration
        
        inst = self.iterate()
        self._result_cache.append(inst)
        self._ct += 1
        self._idx += 1
        return inst
    
    def __len__(self):
        return self.count
    
    @property
    def count(self):
        self.fill_cache()
        return self._ct
    
    def fill_cache(self, n=None):
        counter = -1 if n is None else n
        if counter > 0:
            counter = counter - self._ct

        self._idx = self._ct
        while not self._populated and counter:
            try:
                next(self)
            except StopIteration:
                break
            else:
                counter -= 1
    
    def iterate(self):
        row = self.cursor.fetchone()
        if not row:
            self._populated = True
            if not getattr(self.cursor, 'name', None):
                self.cursor.close()
            raise StopIteration
        elif not self._initialized:
            self.initialize(self.cursor.description)
            self._initailized = True
        return self.process_row(row)
    
    def iterator(self):
        while True:
            yield self.iterate()
    
    def initialize(self, cursor_description):
        i = 0
        n = len(cursor_description)
        self.row_size = n
        self.column_names = []
        self.converters = []
        for i in range(i, n):
            self._initialize_by_name(cursor_description[i][0], i)
    
    def _initialize_by_name(self, name, i):
        # TODO
        self.column_names.append(name)
    
    def process_row(self, row):
        return row

class DictQueryResultWrapper(QueryResultWrapper):
    
    def _make_dict(self, row):
        result = {}
        
        for i in range(self.row_size):
            result[self.column_names[i]] = row[i]
        
        return result
        
    
    def process_row(self, row):
        return self._make_dict(row)