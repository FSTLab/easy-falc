import os
from importlib import import_module
from falcore import FalcModule
import inspect

DIR_MODULES = 'falc_modules'

here = os.path.dirname(os.path.abspath(__file__))
directory_modules = os.path.join(here, DIR_MODULES)

for f in os.listdir(directory_modules):
    if f.startswith('m_') and f.endswith('.py'):
        path = "%s.%s" % (DIR_MODULES, os.path.splitext(f)[0])
        module = import_module(path)
        for name in dir(module):
            try:
                module_instance= getattr(module, name)()
                if isinstance(module_instance, FalcModule):
                    print(name)
            except TypeError:
                pass
