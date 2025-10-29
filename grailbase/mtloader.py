"""Extension loader for filetype handlers.

The extension objects provided by MIMEExtensionLoader objects have four
attributes: parse, embed, add_options, and update_options.  The first two
are used as handlers for supporting the MIME type as primary and embeded
resources.  The last two are (currently) only used for printing.
"""
__version__ = '$Revision: 2.4 $'


import extloader
import string


class MIMEExtensionLoader(extloader.ExtensionLoader):
    """An extension loader for MIME type handlers.

    This class extends ExtensionLoader to find and load handlers for MIME
    types. It converts MIME type strings into module names.
    """
    def find(self, name):
        """Finds a handler for a given MIME type.

        Args:
            name: The MIME type string (e.g., 'text/html').

        Returns:
            A MIMETypeExtension object for the handler, or None if not
            found.
        """
        new_name = name.replace("-", "_")
        major, minor = tuple(new_name.split("/"))
        if minor:
            modname = "%s_%s" % (major, minor)
        else:
            modname = major
        mod = self.find_module(modname)
        ext = None
        if not mod and modname != major:
            ext = self.get(major + "/")
        elif mod:
            ext = MIMETypeExtension(name, mod, modname)
        return ext


class MIMETypeExtension:
    """Represents a handler for a specific MIME type.

    This class encapsulates the functions provided by a MIME type handler
    module, such as parsing and embedding.

    Attributes:
        type: The MIME type string.
        parse: The function for parsing the MIME type as a primary resource.
        embed: The function for embedding the MIME type.
        add_options: A function for adding printing options.
        update_settings: A function for updating printing settings.
    """
    def __init__(self, type, mod, modname):
        """Initializes the MIMETypeExtension.

        Args:
            type: The MIME type string.
            mod: The handler module.
            modname: The name of the handler module.
        """
        self.type = type
        self.__load_attr(mod, "parse_" + modname, "parse")
        self.__load_attr(mod, "embed_" + modname, "embed")
        self.__load_attr(mod, "add_options")
        self.__load_attr(mod, "update_settings")

    def __repr__(self):
        """Returns a string representation of the extension."""
        classname = self.__class__.__name__
        modulename = self.__class__.__module__
        if self.parse and self.embed:
            flags = " [displayable, embeddable]"
        elif self.embed:
            flags = " [embeddable]"
        elif self.parse:
            flags = " [displayable]"
        else:
            # not very useful, now is it?
            flags = ""
        return "<%s.%s for %s%s>" % (modulename, classname, self.type, flags)

    def __load_attr(self, mod, name, as=None):
        """Loads an attribute from the handler module.

        Args:
            mod: The handler module.
            name: The name of the attribute to load.
            as: An optional alternative name for the attribute on this object.
        """
        as = as or name
        if hasattr(mod, name):
            v = getattr(mod, name)
        else:
            v = None
        setattr(self, as, v)
