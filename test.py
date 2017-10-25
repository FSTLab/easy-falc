from importlib import import_module
import os

class Falc:
    DIRECTORY_MODULES = 'falc-modules'

    def __init__(self):
        self.modules = self.init_modules()


    def init_modules(self):
        modules = []
        print("Loading modules:")
        for f in os.listdir(Falc.DIRECTORY_MODULES):
            if f.startswith('m_') and f.endswith('.py'):
                path = "%s.%s" % (Falc.DIRECTORY_MODULES, os.path.splitext(f)[0])
                modules.append(import_module(path))
        return modules

falc = Falc()
for m in falc.modules:
    print(m.process("yolo"))
