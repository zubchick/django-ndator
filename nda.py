# -*- coding: utf-8 -*-

from django.core.management.base import CommandError
from random import randint
from StringIO import StringIO

class NdaModel(object):

    @classmethod
    def fields_for_nda(cls):
        """
        Return a ``List`` contaiining field for the model
        that decared in Meta

        if in Meta ``fields`` or/and ``exclude``:

        ``fields`` is an optional list of field names. If provided, only the named
        fields will be included in the returned fields.

        ``exclude`` is an optional list of field names. If provided, the named
        fields will be excluded from the returned fields, even if they are listed
        in the ``fields`` argument.
        """
        try:
            model = cls.Meta.model
        except AttributeError:
            raise CommandError("Specify model in `Meta` class")

        fields = getattr(cls.Meta, 'fields', None)
        exclude = getattr(cls.Meta, 'exclude', None)
        opts = model._meta
        field_list = []

        for f in opts.fields:
            if fields is not None and not f.name in fields:
                continue
            if exclude and f.name in exclude:
                continue
            if f.auto_created:
                continue
            if f.rel:
                continue
            field_list.append(f)

        return field_list

    @classmethod
    def map_fields(cls, map):
        """
        Return dict {ModelField: NdaModelField, ...}
        """
        fields = cls.fields_for_nda()

        for f in fields:
            pass


class NdaField(object):
    def __init__(self, source_file=None):
        if source_file:
            with open(source_file) as f:
                self.source = StringIO(f.read())

    def obfuscate(self, value):
        return value


class IntegerNda(NdaField):
    def __init__(self, min_value=None, max_value=None):
        self.min = min_value
        self.max = max_value

    def obfuscate(self, value):
        if not (self.min and self.max):
            len_ = len(str(value)) - 1
            res = randint(10 ** len_, 10 ** (len_ + 1) - 1)
        else:
            res = randint(self.min, self.max)

        return res


class BooleanNda(NdaField):
    def obfuscate(self, value):
        return bool(randint(0, 1))


class CharNda(NdaField):
    def __init__(self, source_file='texts/lorem.txt',
                 min_len=None, max_len=None):
        super(CharNda, self).__init__(source_file)
        self.min = min_len
        self.max = max_len

    def obfuscate(self, value):
        text = self.source.read()
        if self.min and self.max:
            res = text[:randint(self.min, self.max)]
        elif self.max:
            res = text[:randint(1, self.max)]
        elif self.min:
            res = text[:randint(self.min, len(text))]
        else:
            res = text[:randint(0, len(text))]

        return res


class FirsNameNda(NdaField):
    def __init__(self, source_file='texts/names.txt', sep=' '):
        super(CharNda, self).__init__(source_file)
        self.sep = sep
        # part: 0 - firstname, 1 - lastname, 2 - middlename
        self.part = 0

    def obfuscate(self, value):
        """ source file shuld be in
        <firstname><separator><lastname><separator><middlename>
        """
        text_lines = self.source.read().splitlines()

        return text_lines[randint(0, len(text_lines)-1)].split(self.sep)[self.part]


class LastNameNda(FirsNameNda):
    def __init__(self, source_file='texts/names.txt', sep=' '):
        super(LastNameNda, self).__init__(source_file)
        # part: 0 - firstname, 1 - lastname, 2 - middlename
        self.part = 1


class MiddleNameNda(FirsNameNda):
    def __init__(self, source_file='texts/names.txt', sep=' '):
        super(LastNameNda, self).__init__(source_file)
        # part: 0 - firstname, 1 - lastname, 2 - middlename
        self.part = 2

