# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.db import models

from optparse import make_option
from ndator.nda import NdaModel, finder
import sys

out = sys.stdout


def autoconvert_to_nda(model):
    """ Auto convert django model to NdaModel """
    meta = type('Meta', (), {'model': model})
    return type(model.__name__ + 'Nda', (NdaModel,), {'Meta': meta})


class Command(BaseCommand):
    help = ""
    requires_model_validation = False
    db_module = 'django.db'

    option_list = BaseCommand.option_list + (
        make_option('--allauto', action='store_true', dest='allauto',
                    default=False, help='Try to make obfuscation with default'
                    'settings'),
        make_option('--noinput', action='store_true', dest='noinput',
                    default=False, help='Do NOT ask any questions '
                                        'before obfuscation'),
        )

    def handle(self, *args, **options):
        allauto = options.get('allauto')
        requested_models = args

        if requested_models and allauto:
            msg = ("YOU SHALL NOT PASS --allauto and "
                   "Nda Model names at the same time")
            raise CommandError(msg)

        if not options.get('noinput'):
            msg = ("After this step all information in models"
                   " will be obfuscated"
                   "\nAre you realy sure? (yes/no): ")
            answer = raw_input(msg).upper()
            while answer != 'YES':
                if answer == 'NO':
                    return
                answer = raw_input('Please enter either "yes" or "no": ')
                answer = answer.upper()
            else:
                print

        if not allauto:
            models_for_nda = finder.find_nda_models()
            models_for_nda = filter(
                lambda nda_model: nda_model.__name__ in requested_models,
                models_for_nda
            )
        else:
            models_for_nda = [autoconvert_to_nda(m) for m
                              in models.get_models()]

        excluded = {}
        for m in models_for_nda:
            name = m.Meta.model.__name__

            # collect excluded fields
            exc = m.excluded_fields()
            if exc:
                excluded[name] = exc

            div = int(m.Meta.model.objects.count() / 20) + 1
            objects = m.Meta.model.objects.all()

            # main loop
            print name,
            for i, obj in enumerate(objects):
                m(obj).obfuscation()

                # progressbar :)
                if not i % div:
                    out.write('.')
                    out.flush()
            else:
                out.write('\n')

        print
        # models and fields that didn't obfuscate
        all_models = set([m.__name__ for m in models.get_models()])
        use_models = set([m.Meta.model.__name__ for m in models_for_nda])
        excluded_models = all_models - use_models

        # display excluded
        print 'These fields were not obfuscated:'
        for name, items in excluded.items():
            print name
            for item in sorted(items):
                print '    ' + item
            print

        print 'Models that were not obfuscated:'
        for model in excluded_models:
            print model
