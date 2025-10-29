"""Application base class."""
__version__ = '$Revision: 2.2 $'

import os
import mimetypes
import regex
import string
import utils


class Application:
    """The base class for the Grail application.

    This class provides the basic application infrastructure, including
    preferences management, icon path setup, and MIME type guessing.

    Attributes:
        prefs: The preferences object for the application.
        graildir: The path to the user's .grail directory.
        iconpath: A list of paths to search for icons.
    """
    def __init__(self, prefs=None):
        """Initializes the Application.

        Args:
            prefs: An optional preferences object. If not provided, a new
                one is created.
        """
        utils._grail_app = self
        if prefs is None:
            import GrailPrefs
            self.prefs = GrailPrefs.AllPreferences()
        else:
            self.prefs = prefs
        self.graildir = utils.getgraildir()
        user_icons = os.path.join(self.graildir, 'icons')
        utils.establish_dir(self.graildir)
        utils.establish_dir(user_icons)
        self.iconpath = [
            user_icons, os.path.join(utils.get_grailroot(), 'icons')]
        #
        self.__loaders = {}
        #
        # Add our type map file to the set used to initialize the shared map:
        #
        typefile = os.path.join(self.graildir, "mime.types") 
        mimetypes.init(mimetypes.knownfiles + [typefile])

    def get_loader(self, name):
        """Gets a loader by name.

        Args:
            name: The name of the loader to get.

        Returns:
            The loader object.
        """
        return self.__loaders[name]

    def add_loader(self, name, loader):
        """Adds a loader to the application.

        Args:
            name: The name of the loader.
            loader: The loader object to add.
        """
        localdir = os.path.join(*name.split("."))
        userdir = os.path.join(self.graildir, localdir)
        loader.add_directory(userdir)
        self.__loaders[name] = loader


    #######################################################################
    #
    #  Misc. support.
    #
    #######################################################################

    def exception_dialog(self, message="", *args):
        """Displays an exception dialog.

        This method is intended to be overridden by subclasses.

        Args:
            message: The message to display in the dialog.
            *args: Additional arguments.
        """
        raise RuntimeError("Subclass failed to implement exception_dialog().")


    import re
    __data_scheme_re = re.compile(
        "data:([^,;]*)(;([^,]*)|),", re.IGNORECASE)

    def guess_type(self, url):
        """Guesses the MIME type of a file based on its URL.

        This method can handle "data:" URLs as well as standard file URLs.

        Args:
            url: The URL to guess the type of.

        Returns:
            A tuple of (type/subtype, encoding) or (None, None) if the type
            cannot be guessed.
        """
        match = self.__data_scheme_re.match(url)
        if match:
            scheme = match.group(1) or "text/plain"
            return scheme.lower(), match.group(3)
        return mimetypes.guess_type(url)
