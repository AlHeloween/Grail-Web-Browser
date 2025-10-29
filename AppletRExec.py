"""Restricted execution for Applets."""


import SafeDialog
import SafeTkinter
import os
from rexec import RExec, RHooks
import string
import sys
import tempfile
import types
import urllib
from urllib import parse as urlparse


def is_url(p):
    """Checks if a path is a URL.

    Args:
        p: The path to check.

    Returns:
        The scheme if it is a URL, otherwise None.
    """
    u = urlparse.urlparse(p)
    #
    # Unfortunately path names on the MAC and Windows parse
    # similarly to URL's.  We currently have to not recognize
    # URL's that have single letter scheme identifiers because
    # they can be confused with the drive letter component
    # of a disk path on these platforms.  
    if u[0] and len(u[0]) > 1:
        return u[0]
    return u[1]


class AppletRHooks(RHooks):
    """Restricted execution hooks for applets.

    This class overrides some of the default RHooks methods to handle URLs
    and provide a sandboxed environment for applets.
    """

    def path_join(self, p1, p2):
        """Joins two path components, handling URLs correctly."""
        if is_url(p1) or is_url(p2):
            if '/' not in p2 and '.' not in p2:
                # Assume it's a directory -- needed for package loading
                p2 = p2 + "/"
            return urlparse.urljoin(p1, p2)
        else:
            return RHooks.path_join(self, p1, p2)

    def path_isdir(self, p):
        """Checks if a path is a directory, handling URLs correctly."""
        if is_url(p):
            return p[-1:] == "/"
        else:
            return RHooks.path_isdir(self, p)

    def openfile(self, p, mode='r', buf=-1):
        """Opens a file, handling URLs correctly.

        This method is used by the import mechanism to read modules. It
        restricts remote access to .py files only.
        """
        # Only used to read modules
        if is_url(p):
            # Avoid hitting the remote server with every suffix
            # in the suffix list (.pyc, .so, module.so).
            # We can't strip these from the suffix list, since
            # (at least under certain circumstances) shared libs
            # are okay when found on the local file system.
            if p[-3:] != '.py':
                raise IOError("Only Python modules may be read remotely")
            return self.openurl(p, mode, buf)
        else:
            return open(p, mode, buf)

    def openurl(self, p, mode='r', buf=-1):
        """Opens a URL for reading.

        This method uses the application's URL opening mechanism.
        """
        if mode not in ('r', 'rb'):
            raise IOError("Can't open URL for writing")
        app = self.rexec.app
        if not app:
            # Fall back for test mode
            return urllib.urlopen(p)
        # Always specify reload since modules are already cached --
        # when we get here it must either be the first time for
        # this module or the user has requested to reload the page.
        api = self.rexec.app.open_url(p, 'GET', {}, reload=1)
        errcode, errmsg, params = api.getmeta()
        if errcode != 200:
            api.close()
            raise IOError, errmsg
        return PseudoFile(api)


class PseudoFile:
    """A file-like object that wraps a URL API object.

    This class provides a file-like interface for reading data from a URL.

    Attributes:
        api: The URL API object.
        buf: A buffer for the data read from the URL.
        done: A flag indicating whether the end of the stream has been reached.
    """

    # XXX Is this safe?
    # XXX Is this sufficient?

    def __init__(self, api):
        """Initializes the PseudoFile.

        Args:
            api: The URL API object.
        """
        self.api = api
        self.buf = ''
        self.done = 0

    def close(self):
        """Closes the file and the underlying URL API object."""
        api = self.api
        self.api = self.buf = self.done = None
        if api:
            api.close()

    def read(self, n=-1):
        """Reads data from the file.

        Args:
            n: The number of bytes to read. If -1, reads until the end of
                the stream.

        Returns:
            The data read from the file as a string.
        """
        if n < 0:
            n = sys.maxsize
        while len(self.buf) < n and not self.done:
            self.fill(min(n - len(self.buf), 1024*8))
        data, self.buf = self.buf[:n], self.buf[n:]
        return data

    def readlines(self):
        """Reads all lines from the file.

        Returns:
            A list of strings, where each string is a line from the file.
        """
        list = []
        while 1:
            line = self.readline()
            if not line: break
            list.append(line)
        return list

    def readline(self):
        """Reads a single line from the file.

        Returns:
            A string containing the line, or an empty string if the end of
            the file is reached.
        """
        while '\n' not in self.buf and not self.done:
            self.fill()
        i = string.find(self.buf, '\n')
        if i < 0:
            i = len(self.buf)
        else:
            i = i+1
        data, self.buf = self.buf[:i], self.buf[i:]
        return data

    def fill(self, n = 512):
        """Fills the buffer with data from the URL.

        Args:
            n: The number of bytes to read.
        """
        data = self.api.getdata(n)
        if data:
            self.buf = self.buf + data
        else:
            self.done = 1


class AppletRExec(RExec):
    """A restricted execution environment for applets.

    This class provides a sandboxed environment for running applet code. It
    restricts access to modules and functions, and provides surrogate objects
    for things like the file system.

    Attributes:
        app: The main application object.
        appletgroup: The applet group this RExec object belongs to.
        backup_modules: A dictionary of modules that have been backed up
            during a reload.
        special_modules: A list of modules that are special to the RExec
            environment.
    """

    # Allow importing the ILU Python runtime
    ok_builtin_modules = RExec.ok_builtin_modules + ('iluPr',)

    # Remove posix primitives except
    ok_posix_names = ('error',)

    def __init__(self, hooks=None, verbose=1, app=None, group=None):
        """Initializes the AppletRExec.

        Args:
            hooks: An optional RHooks object.
            verbose: The verbosity level.
            app: The main application object.
            group: The applet group.
        """
        self.app = app
        self.appletgroup = group or "."
        self.backup_modules = {}
        if not hooks: hooks = AppletRHooks(self, verbose)
        RExec.__init__(self, hooks, verbose)
        self.modules['Dialog'] = SafeDialog
        self.modules['Tkinter'] = SafeTkinter
        self.special_modules = self.modules.keys()
        self.save_files()
        self.set_files()
        # Don't give applets the real SystemExit, since it exits Grail!
        self.modules['__builtin__'].SystemExit = "SystemExit"

    # XXX The path manipulations below are not portable to the Mac or PC

    def set_urlpath(self, url):
        """Adds a URL to the module search path."""
        self.reset_urlpath()
        path = self.modules['sys'].path
        path.append(url)

    def reset_urlpath(self):
        """Resets the module search path to its original state."""
        path = self.modules['sys'].path
        path[:] = self.get_url_free_path()

    def get_url_free_path(self):
        """Gets the module search path without any URLs."""
        path = self.modules['sys'].path
        return filter(lambda x: not is_url(x), path)

    # XXX It would be cool if make_foo() would be invoked on "import foo"

    def make_initial_modules(self):
        """Creates the initial set of modules for the RExec environment."""
        RExec.make_initial_modules(self)
        self.make_al()
        self.make_socket()
        self.make_sunaudiodev()
        self.make_types()
        self.make_iluRt()
        self.make_os()

    def make_os(self):
        """Creates a surrogate 'os' module."""
        from Bastion import Bastion
        s = OSSurrogate(self)
        b = Bastion(s)
        b.path = Bastion(s.path)
        b.name = s.name
        b.curdir = s.curdir
        b.pardir = s.pardir
        b.sep = s.sep
        b.pathsep = s.pathsep
        b.environ = s.environ
        b.error = s.error
        self.modules['os'] = self.modules[os.name] = b
        self.modules['ospath'] = self.modules[os.name + 'path'] = b.path

    def make_osname(self):
        """Does nothing. This is here to override the base class method."""
        pass

    def make_iluRt(self):
        """Creates a surrogate 'iluRt' module."""
        try:
            import iluRt
        except ImportError:
            return
        m = self.copy_except(iluRt, ())
 
    def make_al(self):
        """Creates a surrogate 'al' module."""
        try:
            import al
        except ImportError:
            return
        m = self.copy_except(al, ())
 
    def make_socket(self):
        """Creates a surrogate 'socket' module."""
        try:
            import socket
        except ImportError:
            return
        m = self.copy_except(socket, ('fromfd',))
        # XXX Ought to only allow connections to host from which applet loaded

    def make_sunaudiodev(self):
        """Creates a surrogate 'sunaudiodev' module."""
        try:
            import sunaudiodev
        except ImportError:
            return
        m = self.copy_except(sunaudiodev, ())

    def make_types(self):
        """Creates a surrogate 'types' module."""
        m = self.copy_except(types, ())

    def r_open(self, file, mode='r', buf=-1):
        """Restricted version of open()."""
        return self.modules['os'].fopen(file, mode, buf)

    # Cool reload hacks.  XXX I'll explain this some day...

    def set_reload(self):
        """Prepares the RExec environment for a reload.

        This method backs up all non-special modules so they can be reloaded.
        """
        for mname, module in self.modules.items():
            if mname not in self.special_modules and \
               mname not in self.ok_builtin_modules and \
               mname not in self.ok_dynamic_modules:
                self.backup_modules[mname] = module
                del self.modules[mname]

    def clear_reload(self):
        """Clears the reload state."""
        self.backup_modules = {}

    def add_module(self, mname):
        """Adds a module to the RExec environment.

        If the module is in the backup dictionary, it is restored from there.
        Otherwise, it is loaded normally.

        Args:
            mname: The name of the module to add.

        Returns:
            The module object.
        """
        if mname in self.modules:
            return self.modules[mname]
        if mname in self.backup_modules:
            self.modules[mname] = m = self.backup_modules[mname]
            self.backup_modules[mname]
            return m
        return RExec.add_module(self, mname)


class OSSurrogate:
    """A surrogate for the 'os' module.

    This class provides a restricted version of the 'os' module for applets.
    It restricts file access to a specific directory and provides a safe
    subset of the 'os' module's functions.
    """

    # Class variables (these become public by explicit assignment in
    # make_os()).

    name = os.name
    curdir = os.curdir
    pardir = os.pardir
    sep = os.sep
    pathsep = os.pathsep
    error = os.error

    # Private methods

    def __init__(self, rexec):
        """Initializes the OSSurrogate.

        Args:
            rexec: The AppletRExec instance.
        """
        self.rexec = rexec
        self.app = rexec.app
        self.appletsdir = os.path.join(self.app.graildir, "applets")
        self.home = os.path.normcase(
            os.path.join(self.appletsdir,
                         group2dirname(self.rexec.appletgroup)))
        self.home_made = 0
        self.pwd = self.home
        # Self environ is public
        self.environ = {
            'HOME': self.home,
            'LOGNAME': 'nobody',
            'PWD': self.pwd,
            'TMPDIR': self.home,
            'USER': 'nobody',
            }
        self.path = OSPathSurrogate(self)

    def _path(self, path, writing=0, error=os.error):
        """Converts and checks a pathname.

        This method implements the security policy for file access.

        Args:
            path: The path to check.
            writing: A flag indicating whether the file is being opened for
                writing.
            error: The exception to raise on error.

        Returns:
            The normalized, absolute path.

        Raises:
            error: If the path is not allowed.
        """
        path = os.path.join(self._pwd(), path)
        path = os.path.normpath(path)
        if writing:
            n = len(self.home)
            if not(path[:n] == self.home and path[n:n+1] == os.sep):
                raise error("can't write outside applet's own directory")
            head, tail = os.path.split(path)
            if tail[:1] == "." and tail not in (os.curdir, os.pardir):
                raise error("can't write filenames beginning with '.'")
        return path

    def _pwd(self):
        """Returns the current working directory, creating it if necessary."""
        if self.pwd == self.home:
            return self._home()
        return self.pwd

    def _home(self):
        """Creates the applet's home directory if it does not exist."""
        if not self.home_made:
            if not os.path.exists(self.home):
                if not os.path.exists(self.appletsdir):
                    os.mkdir(self.appletsdir, 0777)
                os.mkdir(self.home, 0777)
            self.home_made = 1
        return self.home

    # Public, applet visible methods (as functions in module os).
    # IN ALPHABETICAL ORDER, PLEASE!

    def fopen(self, path, mode='r', bufsize=-1):
        """A restricted version of open()."""
        path = self._path(path, writing=(mode[:1] != 'r'), error=IOError)
        return open(path, mode, bufsize)

    def getcwd(self):
        """Gets the current working directory."""
        return self._pwd()

    def getpid(self):
        """Returns a fake process ID.

        Since TMPDIR is set to the applet's home dir anyway, there's
        no need for this to be randomly changing.
        """
        return 666

    def listdir(self, path):
        """Lists the contents of a directory."""
        return os.listdir(self._path(path))

    def unlink(self, path):
        """Deletes a file."""
        path = self._path(path, 1)
        os.unlink(path)


TEMPLATE1 = """
def %(name)s(self, arg):
    return os.path.%(name)s(arg)
"""
TEMPLATE2 = """
def %(name)s(self, a1, a2):
    return os.path.%(name)s(a1, a2)
"""
TEMPLATE3 = """
def %(name)s(self, path):
    return os.path.%(name)s(self.os._path(path))
"""

class OSPathSurrogate:
    """A surrogate for the 'os.path' module."""

    def __init__(self, ossurrogate):
        """Initializes the OSPathSurrogate.

        Args:
            ossurrogate: The OSSurrogate instance.
        """
        self.os = ossurrogate

    for name in ('normcase', 'isabs', 'split', 'splitext',
                 'splitdrive', 'basename', 'dirname', 'normpath'):
        exec TEMPLATE1 % {'name': name}

    for name in ('commonprefix', 'samestat'):
        exec TEMPLATE2 % {'name': name}

    def join(self, *args):
        """Joins path components."""
        return os.path.join(*args)

    for name in ('exists', 'isdir', 'isfile', 'islink', 'ismount'):
        exec TEMPLATE3 % {'name': name}

    def samefile(self, p1, p2):
        """Checks if two paths refer to the same file."""
        return os.path.samefile(self.os._path(p1), self.os._path(p2))

    def walk(self, top, func, arg):
        """Walks a directory tree."""
        return os.path.walk(self.os._path(top), func, arg)

    def expanduser(self, path):
        """Expands a path containing a tilde."""
        if path[:1] == '~' and path[1:2] == os.sep:
            path = self.os.environ['HOME'] + path[1:]
        return path


def group2dirname(group):
    """Converts an applet group name to a unique and safe directory name.

    This function takes a group name and creates a directory name that is
    short, unique, and safe for all file systems. It does this by taking
    a truncated and sanitized version of the group name and appending a
    checksum.

    Args:
        group: The applet group name.

    Returns:
        A safe and unique directory name as a string.
    """
    import regsub, md5
    sum = md5.new(group).digest()
    path = regsub.gsub('[:/\\]+', '_', group)
    if len(path) > 15:
        path = path[:7] + '_' + path[-7:]
    path = path + hexstring(sum[:8])
    return path


def hexstring(s):
    """Converts a string to a hex representation.

    Args:
        s: The string to convert.

    Returns:
        A string of hexadecimal characters.
    """
    return "%02x"*len(s) % tuple(map(ord, s))
