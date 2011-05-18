# -*- coding: utf-8 -*-

from django.core.management.base import NoArgsCommand, CommandError
from django.db import  DEFAULT_DB_ALIAS, models

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


class Command(NoArgsCommand):
    help = ""
    requires_model_validation = False
    db_module = 'django.db'

    option_list = NoArgsCommand.option_list + (
        make_option('--database', action='store', dest='database',
                    default=DEFAULT_DB_ALIAS, help='Nominates a database to '
                    'introspect.  Defaults to using the "default" database.'),
        make_option('--allauto', action='store_true', dest='allauto',
                    default=False, help='Try to make obfuscation with default'
                    'settings'),
        )

    def handle_noargs(self, **options):
        allauto = options.get('allauto')
        if not allauto:
            models_for_nda = get_nda_models()
        else:
            models_for_nda = models.get_models()

        # print models_for_nda
        import ipdb;ipdb.set_trace()
        for m in models_for_nda:
            print "%s:" % m
            print map(lambda x: "%s: %s" % (x.name, x), m.fields_for_nda())


