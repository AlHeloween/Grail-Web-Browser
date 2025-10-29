"""Several useful routines that isolate some of the weirdness of Grail-based
applications.
"""
__version__ = '$Revision: 1.3 $'

import os
import string

# TBD: hack!  grail.py calculates grail_root, which would be
# convenient to export to extensions, but you can't `import grail' or
# `import __main__'.  grail.py isn't designed for that.  You could
# `from grail import grail_root' but that's kind of gross.  This
# global holds the value of grail_root which can be had with
# grailutil.get_grailroot()
_grail_root = None
_grail_app = None


# XXX Unix specific stuff
# XXX (Actually it limps along just fine for Macintosh, too)

def getgraildir():
    """Gets the path to the user's .grail directory.

    This is determined by the GRAILDIR environment variable, or defaults to
    ~/.grail.

    Returns:
        The path to the .grail directory as a string.
    """
    return getenv("GRAILDIR") or os.path.join(gethome(), ".grail")


def get_grailroot():
    """Gets the root directory of the Grail installation.

    Returns:
        The path to the Grail root directory as a string.
    """
    return _grail_root


def get_grailapp():
    """Gets the main application object.

    Returns:
        The Application object.
    """
    return _grail_app


def gethome():
    """Gets the user's home directory.

    This function tries to determine the home directory from environment
    variables or the password database.

    Returns:
        The path to the user's home directory as a string.
    """
    try:
        home = getenv("HOME")
        if not home:
            import pwd
            user = getenv("USER") or getenv("LOGNAME")
            if not user:
                pwent = pwd.getpwuid(os.getuid())
            else:
                pwent = pwd.getpwnam(user)
            home = pwent[6]
        return home
    except (KeyError, ImportError):
        return os.curdir


def getenv(s):
    """Gets an environment variable.

    Args:
        s: The name of the environment variable.

    Returns:
        The value of the environment variable, or None if it is not set.
    """
    return os.environ.get(s)


def which(filename, searchlist=None):
    """Finds a file in a list of directories.

    This is similar to the Unix `which` command.

    Args:
        filename: The name of the file to find.
        searchlist: An optional list of directories to search. If not
            provided, `sys.path` is used.

    Returns:
        The full path to the file, or None if it is not found.
    """
    if searchlist is None:
        import sys
        searchlist = sys.path
    for dir in searchlist:
        found = os.path.join(dir, filename)
        if os.path.exists(found):
            return found
    return None


def establish_dir(dir):
    """Ensure existence of DIR, creating it if necessary.

    Returns 1 if successful, 0 otherwise."""
    if os.path.isdir(dir):
        return 1
    head, tail = os.path.split(dir)
    if not establish_dir(head):
        return 0
    try:
        os.mkdir(dir, 0777)
        return 1
    except os.error:
        return 0


def conv_mimetype(type):
    """Converts a MIME media type string to a tuple.

    Args:
        type: The MIME type string (e.g., 'text/html; charset=utf-8').

    Returns:
        A tuple of (type/subtype, options_dict).
    """
    if not type:
        return None, {}
    if ';' in type:
        i = type.index(';')
        opts = _parse_mimetypeoptions(type[i + 1:])
        type = type[:i]
    else:
        opts = {}
    fields = type.lower().split('/')
    if len(fields) != 2:
        raise ValueError("Illegal media type specification.")
    type = '/'.join(fields)
    return type, opts


def _parse_mimetypeoptions(options):
    """Parses MIME type options.

    Args:
        options: A string of MIME type options (e.g., 'charset=utf-8').

    Returns:
        A dictionary of the options.
    """
    opts = {}
    options = options.strip()
    while options:
        if '=' in options:
            pos = options.find('=')
            name = options[:pos].strip().lower()
            value = options[pos + 1:].strip()
            options = ''
            if ';' in value:
                pos = value.find(';')
                options = value[pos + 1:].strip()
                value = value[:pos].strip()
            if name:
                opts[name] = value
        else:
            options = None
    return opts
