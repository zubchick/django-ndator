import inspect

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

from ndator.nda import NdaModel


GLOBAL_MODULE_SETTING = 'NDATOR_GLOBAL_MODULE'
GLOBAL_MODULE_DEFAULT = 'ndamodels'


def _get_global_module():
    """
    Import and return global ndamodels module from location specified
    in settings. If not specified, use default location.
    """
    if hasattr(settings, GLOBAL_MODULE_SETTING):
        module_specified = True
        module_name = getattr(settings, GLOBAL_MODULE_SETTING)
    else:
        module_name = GLOBAL_MODULE_DEFAULT
        module_specified = False

    try:
        return import_module(module_name)
    except ImportError:
        if module_specified:
            message = ('Module "%s" specified in %s setting could not '
                       'be imported') % (module_name, GLOBAL_MODULE_SETTING)
            raise ImproperlyConfigured(message)


def _get_app_modules():
    """
    Collect and import all modules named "ndamodule" in every
    application package and return as a list.
    """
    module_list = []
    for app_module in settings.INSTALLED_APPS:
        nda_module = '.'.join([app_module, 'ndamodels'])
        try:
            module_list.append(import_module(nda_module))
        except ImportError:
            pass
    return module_list


def _extract_models(module):
    """ Return list of NdaModel classes in specified module """
    class_list = []
    for elem in dir(module):
        obj = getattr(module, elem)

        if (inspect.isclass(obj) and
                issubclass(obj, NdaModel)
                and obj is not NdaModel):
            class_list.append(obj)

    return class_list


def find_nda_models():
    """ Return list of NdaModel classes from all configured sources """
    module_list = []

    global_module = _get_global_module()
    if global_module:
        module_list.append(global_module)

    if getattr(settings, 'NDATOR_SEARCH_IN_APPS', False):
        for app_module in _get_app_modules():
            module_list.append(app_module)

    class_list = []
    for module in module_list:
        for cls in _extract_models(module):
            class_list.append(cls)

    return class_list
