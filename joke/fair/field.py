#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

class FieldDescriptor(object):
    # Fields are exposed as descriptors in order to control access to the
    # underlying "raw" data.
    def __init__(self, field):
        self.field = field
        self.att_name = self.field.name

    def __get__(self, instance, instance_type=None):
        if instance is not None:
            return instance._data.get(self.att_name)
        return self.field

    def __set__(self, instance, value):
        instance._data[self.att_name] = value
        instance._dirty.add(self.att_name)


class Field(object):
    _field_counter = 0
    _order = 0
    db_field = 'unknown'
    def __init__(self,  null=False, index=False, unique=False,
                 verbose_name=None, help_text=None, db_column=None,
                 default=None, choices=None, primary_key=False, sequence=None,
                 constraints=None, schema=None, undeclared=False, **kwargs):
        self.null = null
        self.index = index
        self.unique = unique
        self.verbose_name = verbose_name
        self.help_text = help_text
        self.db_column = db_column
        self.default = default
        self.choices = choices  # Used for metadata purposes, not enforced.
        self.primary_key = primary_key
        self.sequence = sequence  # Name of sequence, e.g. foo_id_seq.
        self.constraints = constraints  # List of column constraints.
        self.schema = schema  # Name of schema, e.g. 'public'.
        self.undeclared = undeclared  # Whether this field is part of schema.
        # Used internally for recovering the order in which Fields were defined
        # on the Model class.
        Field._field_counter += 1
        self._order = Field._field_counter
        self._sort_key = (self.primary_key and 1 or 2), self._order
                
        self._is_bound = False  # Whether the Field is "bound" to a Model.
        
        super(Field, self).__init__()
        
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def add_to_class(self, model_class, name):
        """
        Hook that replaces the `Field` attribute on a class with a named
        `FieldDescriptor`. Called by the metaclass during construction of the
        `Model`.
        """
        self.name = name
        self.model_class = model_class
        self.db_column = self.db_column or self.name
        if not self.verbose_name:
            self.verbose_name = re.sub('_+', ' ', name).title()

        model_class._meta.add_field(self)
        setattr(model_class, name, FieldDescriptor(self))
        self._is_bound = True


class IntegerField(Field):
    db_field = 'int'
    coerce = int


class TextField(Field):
    db_field = 'text'


class BlobField(Field):
    db_field = 'blob'

# sqlite
class RealField(Field):
    db_field = 'real'

class DateTimeField(Field):
    db_field = 'datetime'

class PrimaryKeyField(Field):
    pass
