# -*- coding: utf-8 -*-

from django.core.management.base import NoArgsCommand, CommandError
from django.db import models

from optparse import make_option
from ndator.nda import NdaModel, finder
import sys

out = sys.stdout


def autoconvert_to_nda(model):
    """ Auto convert django model to NdaModel """
    meta = type('Meta', (), {'model': model})
    return type(model.__name__ + 'Nda', (NdaModel,), {'Meta': meta})


class Command(NoArgsCommand):
    help = ""
    requires_model_validation = False
    db_module = 'django.db'

    option_list = NoArgsCommand.option_list + (
        make_option('--allauto', action='store_true', dest='allauto',
                    default=False, help='Try to make obfuscation with default'
                    'settings'),
        make_option('--noinput', action='store_true', dest='noinput',
                    default=False, help='Do NOT ask any questions'
                                        'before obfuscation'),
        )

    def handle_noargs(self, **options):
        allauto = options.get('allauto')

        if not options.get('noinput'):
            answ = ''
            msg = ("After this step all information in models"
                   " will be obfuscated"
                   "\nAre you realy sure? (yes/no): ")
            answ = raw_input(msg).upper()
            while answ != 'YES':
                if answ == 'NO':
                    return
                elif answ != 'YES':
                    answ = raw_input('Please enter either "yes" or "no": ')
                    answ = answ.upper()
            else:
                print

        if not allauto:
            models_for_nda = finder.find_nda_models()
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
