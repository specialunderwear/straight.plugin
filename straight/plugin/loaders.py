"""Facility to load plugins."""

import sys
import os

from importlib import import_module


class ModuleLoader(object):
    """Performs the work of locating and loading straight plugins.
    
    This looks for plugins in every location in the import path.
    """

    def _findPluginFilePaths(self, namespace):
        already_seen = set()

        # Look in each location in the path
        for path in sys.path:

            # Within this, we want to look for a package for the namespace
            namespace_rel_path = namespace.replace(".", os.path.sep)
            namespace_path = os.path.join(path, namespace_rel_path)
            if os.path.exists(namespace_path):
                for possible in os.listdir(namespace_path):
                    base, ext = os.path.splitext(possible)
                    if base == '__init__' or ext != '.py':
                        continue
                    if base not in already_seen:
                        already_seen.add(base)
                        yield os.path.join(namespace, possible)

    def _findPluginModules(self, namespace):
        for filepath in self._findPluginFilePaths(namespace):
            path_segments = list(filepath.split(os.path.sep))
            path_segments = [p for p in path_segments if p]
            path_segments[-1] = os.path.splitext(path_segments[-1])[0]
            import_path = '.'.join(path_segments)
            yield import_module(import_path)

    def load(self, namespace):
        """Load all modules found in a namespace"""

        modules = self._findPluginModules(namespace)

        return list(modules)


class ObjectLoader(object):
    """Loads classes or objects out of modules in a namespace, based on a
    provided criteria.
   
    The load() method returns all objects exported by the module.
    """

    def __init__(self):
        self.module_loader = ModuleLoader()

    def load(self, namespace):
        modules = self.module_loader.load(namespace)
        objects = []

        for module in modules:
            for attr_name in dir(module):
                if not attr_name.startswith('_'):
                    objects.append(getattr(module, attr_name))
    
        return objects
