# -*- coding: utf-8 -*-

from django.core.management.base import NoArgsCommand, CommandError
from django.db import models

from optparse import make_option
from ndator.nda import NdaModel
import inspect


def get_nda_models():
    """ Return list of NdaModel classes
    from ndamodels.py file
    """
    class_list = []
    try:
        import ndamodels
    except ImportError:
        raise CommandError("Create ndamodels.py in project dir or use --allauto option.")

    for elem in dir(ndamodels):
        obj = getattr(ndamodels, elem)

        if (inspect.isclass(obj) and
            issubclass(obj, NdaModel) and
            obj is not NdaModel):
            class_list.append(obj)

    return class_list

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
        )

    def handle_noargs(self, **options):
        allauto = options.get('allauto')
        answ = ''
        while answ != 'YES':
            answ = raw_input('Are you realy shure? (yes/no): ').upper()
            if answ == 'NO':
                return
            elif answ != 'YES':
                print 'type only yes or no'
        else:
            print

        if not allauto:
            models_for_nda = get_nda_models()
        else:
            models_for_nda = [autoconvert_to_nda(m) for m in models.get_models()]

        for m in models_for_nda:
            print m.Meta.model.__name__,
            div = int(m.Meta.model.objects.count() / 20) + 1
            objects = m.Meta.model.objects.all()
            for i, obj in enumerate(objects, 1):
                m(obj).obfuscation()
                if not i % div:
                    print '.',
            else:
                print
