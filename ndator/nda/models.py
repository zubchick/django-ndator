# -*- coding: utf-8 -*-

from django.core.management.base import CommandError
from fields import (NdaField, IntegerNda, FloatFieldNda, BooleanNda, CharNda,
                    DateNda, DateTimeNda, TimeNda, EmailNda, IPAdressNda,
                    NullBooleanNda, URLNda, SlugNda)
from django.db.models import fields as mfields

class NdaModel(object):

    def __init__(self, instance=None):
        if not isinstance(instance, self.Meta.model):
            raise Exception("`instance` parameter is not an instance of %s class" % self.__class__.__name__)
        self.instance = instance

    @classmethod
    def fields_for_nda(cls):
        """
        Return a ``List`` contaiining field for the model
        that declared in Meta

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
    def excluded_fields(cls):
        ffnda = set([i.name for i in cls.fields_for_nda()])
        try:
            allfields = set([i.name for i in cls.Meta.model._meta.fields])
        except:
            raise CommandError("Specify model in `Meta` class")

        return allfields - ffnda

    @classmethod
    def map_fields(cls):
        """
        mapping django.models to NdaModels
        Return dict {'field': NdaModelField instance, ...}
        """
        fields = cls.fields_for_nda()

        res = {}
        for f in fields:
            current = getattr(cls, f.name, None)
            if current:
                res[f.name] = current
                continue

            if isinstance(f, mfields.BigIntegerField):
                res[f.name] = IntegerNda(min_value=-9223372036854775808,
                                         max_value=9223372036854775807)

            elif isinstance(f, mfields.BooleanField):
                res[f.name] = BooleanNda()

            elif isinstance(f, (mfields.CharField,)):
                res[f.name] = CharNda(max_length=f.max_length)

            elif isinstance(f, mfields.SlugField):
                res[f.name] = SlugNda(max_length=f.max_length)

            elif isinstance(f, mfields.DateField):
                res[f.name] = DateNda()

            elif isinstance(f, mfields.DateTimeField):
                res[f.name] = DateTimeNda()

            elif isinstance(f, mfields.EmailField):
                res[f.name] = EmailNda()

            elif isinstance(f, (mfields.DecimalField, mfields.FloatField)):
                res[f.name] = FloatFieldNda()

            elif isinstance(f, (mfields.PositiveIntegerField,
                                mfields.IntegerField,
                                mfields.SmallIntegerField)):
                res[f.name] = IntegerNda()

            elif isinstance(f, mfields.IPAddressField):
                res[f.name] = IPAdressNda()

            elif isinstance(f, mfields.NullBooleanField):
                res[f.name] = NullBooleanNda()

            elif isinstance(f, mfields.TextField):
                res[f.name] = CharNda(max_length=300)

            elif isinstance(f, mfields.TimeField):
                res[f.name] = TimeNda()

            elif isinstance(f, mfields.URLField):
                res[f.name] = URLNda()

            else:
                res[f.name] = NdaField()

        return res

    def obfuscation(self):
        rules = self.map_fields()
        for field, rule  in rules.items():
            attr = getattr(self.instance, field)
            setattr(self.instance, field, rule.obfuscate(attr))
        self.instance.save()
