import json
import os
from pathlib import Path
from inspect import isclass
from pkgutil import iter_modules
from importlib import import_module


class DictDot(object):
    def __init__(self, dict_):
        self.__dict__.update(dict_)

def Dict2DictDot(d):
    if not isinstance(d, DictDot):
        return json.loads(json.dumps(d), object_hook=DictDot)
    else:
        return d


def verifyConfiguration(cfg):
    return True

def class_import(name):
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def importClasses(_file=None, _name=None, cls_name_pattern=None):
    # iterate through the modules in the current package
    package_dir = Path(_file).resolve().parent

    attribute_tuples = []

    for (module_path, module_name, is_module) in iter_modules([package_dir]):
        # if is_module:
        # import the module and iterate through its attributes
        module = import_module(f"{_name}.{module_name}")
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)

            if isclass(attribute) and (cls_name_pattern in attribute.__name__):
                # Add the class to this package's variables
                # globals()[attribute_name] = attribute
                attribute_tuples += [(attribute_name, attribute)]
    return attribute_tuples


def importModules(_file=None, _name=None):  # ,cls_name_pattern=None):
    # iterate through the modules in the current package
    package_dir = Path(_file).resolve().parent
    module_list = []
    for (module_path, module_name, is_module) in iter_modules([package_dir]):
        # if "__" in module_name:
        #   print('wtf')
        if is_module and ('__' not in module_name):  # (module_name[:2]!='__'): # and (module_name[-2:]!='__'):
            # import the module and iterate through its attributes
            module_list += [f"{_name}.{module_name}"]
            print(f"Imported module -- {is_module} -- from -- {module_path}: {_name}.{module_name}")
    return module_list


def import_package_modules(_file: str, _name: str):
    """
    This logic dynamically discovers and imports any subpackage modules to _file.
    This allows for decorators to be executed.

    :param _file: the file whose directory location will be used to discover the subpackages
    :type _file: str
    :param _name: the module name
    :type _name: str
    """
    data_pkg_dir = os.path.dirname(_file)
    pkgs = [
        (f"{_name}.{pkg}", os.path.join(data_pkg_dir, pkg))
        for pkg in os.listdir(data_pkg_dir)
        if os.path.isdir(os.path.join(data_pkg_dir, pkg)) and not pkg.startswith('_')
    ]

    for pkg_name, pkg_path in pkgs:
        for _, module_name, _ in iter_modules([pkg_path]):
            import_module(f"{pkg_name}.{module_name}")
