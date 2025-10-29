"""Simple extension loader.  Specializations should override the get() method
to do the right thing."""

__version__ = '$Revision: 1.2 $'

import os


class ExtensionLoader:
    """A simple class for loading extensions.

    This class provides a basic mechanism for finding and loading extensions
    (modules) from a given package.

    Attributes:
        __package: The package from which to load extensions.
        __name: The name of the package.
        __extensions: A dictionary of loaded extensions.
    """
    def __init__(self, package):
        """Initializes the ExtensionLoader.

        Args:
            package: The package object from which to load extensions.
        """
        self.__package = package
        self.__name = package.__name__
        self.__extensions = {}

    def get(self, name):
        """Gets an extension by name.

        If the extension is not already loaded, this method will try to find
        and load it.

        Args:
            name: The name of the extension to get.

        Returns:
            The extension module, or None if it cannot be found.
        """
        try:
            ext = self.get_extension(name)
        except KeyError:
            ext = self.find(name)
            if ext is not None:
                self.add_extension(name, ext)
        return ext

    def find(self, name):
        """Finds an extension by name.

        This method can be overridden by subclasses to implement different
        finding strategies.

        Args:
            name: The name of the extension to find.

        Returns:
            The extension module, or None if it cannot be found.
        """
        return self.find_module(name)

    def find_module(self, name):
        """Finds and imports a module.

        Args:
            name: The name of the module to find.

        Returns:
            The imported module, or None if it cannot be imported.
        """
        realname = "%s.%s" % (self.__name, name)
        d = {}
        s = "import %s; mod = %s" % (realname, realname)
        try:
            exec(s, d)
        except ImportError:
            mod = None
        else:
            mod = d["mod"]
        return mod

    def add_directory(self, path):
        """Adds a directory to the package's search path.

        Args:
            path: The directory path to add.

        Returns:
            1 if the path was added, 0 otherwise.
        """
        path = os.path.normpath(os.path.join(os.getcwd(), path))
        if path not in self.__package.__path__:
            self.__package.__path__.insert(0, path)
            return 1
        else:
            return 0

    def add_extension(self, name, extension):
        """Adds a loaded extension to the cache.

        Args:
            name: The name of the extension.
            extension: The extension module.
        """
        self.__extensions[name] = extension

    def get_extension(self, name):
        """Gets a loaded extension from the cache.

        Args:
            name: The name of the extension.

        Returns:
            The extension module.
        """
        return self.__extensions[name]
