"""Implement applet loading, possibly asynchronous."""

import os
import regex
import string
import urllib
import urlparse
from Tkinter import *
from BaseReader import BaseReader
from Bastion import Bastion


# Pattern for valid CODE attribute; group(2) extracts module name
codeprog = regex.compile('^\(.*/\)?\([_a-zA-Z][_a-zA-Z0-9]*\)\.py$')

CLEANUP_HANDLER_NAME = "__cleanup__"


class AppletLoader:
    """Stores information about an applet and handles its loading.

    This class gathers information from the HTML parser about an applet,
    including its code, parameters, and display properties. It then manages
    the process of loading the applet's code, instantiating it, and
    placing it in the document.

    Attributes:
        parser: The HTML parser instance.
        viewer: The viewer object.
        context: The URI context.
        app: The main application object.
        name: The name of the applet.
        classid: The class ID of the applet (for <OBJECT>).
        code: The URL of the applet's code.
        codebase: The base URL for the applet's code.
        width: The width of the applet.
        height: The height of the applet.
        vspace: The vertical space around the applet.
        hspace: The horizontal space around the applet.
        align: The alignment of the applet.
        menu: The name of the menu to create for the applet.
        reload: A flag indicating a reload.
        params: A dictionary of parameters for the applet.
        modname: The name of the applet's module.
        classname: The name of the applet's class.
        codeurl: The full URL to the applet's code.
        parent: The parent widget for the applet.
        module: The applet's module.
        klass: The applet's class.
        instance: The applet instance.
        rexec: The restricted execution object.
    """

    def __init__(self, parser, name=None, classid=None,
                 code=None, codebase=None,
                 width=None, height=None, vspace=0, hspace=0,
                 align=None,
                 menu=None, reload=0):
        """Initializes the AppletLoader.

        Args:
            parser: The HTML parser instance.
            name: The name of the applet.
            classid: The class ID of the applet.
            code: The URL of the applet's code.
            codebase: The base URL for the applet's code.
            width: The width of the applet.
            height: The height of the applet.
            vspace: The vertical space around the applet.
            hspace: The horizontal space around the applet.
            align: The alignment of the applet.
            menu: The name of the menu to create for the applet.
            reload: A flag indicating a reload.
        """
        self.parser = parser
        self.viewer = self.parser.viewer
        self.context = self.viewer.context
        self.app = self.parser.app

        self.name = name
        self.classid = classid
        self.code = code
        self.codebase = codebase
        self.width = width
        self.height = height
        self.vspace = vspace
        self.hspace = hspace
        self.align = align
        self.menu = menu
        self.reload = reload
        
        self.params = {}

        self.modname = None
        self.classname = None
        self.codeurl = None

        self.parent = None
        self.module = None
        self.klass = None
        self.instance = None

        self.rexec = None

        if self.reload:
            self.reload.attach(self)

    def __del__(self):
        """Ensures that the close() method is called when the object is
        destroyed."""
        self.close()

    def close(self):
        """Cleans up all references to external objects."""
        self.parser = self.viewer = self.context = self.app = None
        self.params = {}
        self.modname = self.codeurl = None
        self.parent = self.module = self.klass = self.instance = None
        self.rexec = None
        if self.reload:
            self.reload.detach(self)
        self.reload = None

    def get_rexec(self):
        """Gets or creates the restricted execution object for this applet's
        group.

        Returns:
            The RExec object.
        """
        if not self.rexec:
            key = get_key(self.context)
            cache = self.app.rexec_cache
            if not cache.has_key(key) or not cache[key]:
                from AppletRExec import AppletRExec
                rexec = AppletRExec(hooks=None, verbose=2, app=self.app,
                                    group=key)
                cache[key] = rexec
            self.rexec = cache[key]
        return self.rexec

    def feasible(self):
        """Checks whether the applet should be loaded based on user
        preferences.

        Returns:
            True if the applet should be loaded, False otherwise.
        """
        prefs = self.app.prefs
        mode = prefs.Get("applets", "load")
        if mode == "none":
            return 0
        if mode == "some":
            key = get_key(self.context)
            rawgroups = prefs.Get("applets", "groups")
            groups = map(string.lower, string.split(rawgroups))
            if key not in groups:
                return 0
        if self.code:                   # <APP> or <APPLET>
            return codeprog.match(self.code) == len(self.code)
        else:                           # <OBJECT>
            if self.classid:
                if codeprog.match(self.classid) == len(self.classid):
                    return 1
            if self.codebase:
                if codeprog.match(self.codebase) == len(self.codebase):
                    return 1
            return 0

    def set_param(self, name, value):
        """Sets a parameter for the applet.

        This method attempts to convert the value to a number if possible.

        Args:
            name: The name of the parameter.
            value: The value of the parameter.
        """
        try:
            value = string.atoi(value, 0)
        except string.atoi_error:
            try:
                value = string.atol(value, 0)
            except string.atol_error:
                try:
                    value = string.atof(value)
                except string.atof_error:
                    pass
        self.params[name] = value

    def go_for_it(self):
        """Starts the process of loading and instantiating the applet.

        This method handles both synchronous and asynchronous loading of the
        applet's code. Errors are reported through the application's
        exception dialog.
        """
        try:
            self._go_for_it()
        except:
            self.show_tb()
            self.close()

    def _go_for_it(self):
        """Internal helper for go_for_it()."""
        self.get_defaults()
        self.module = self.get_easy_module(self.modname)
        if self.module:
            # Synchronous loading
            self.klass = getattr(self.module, self.classname)
            self.parent = self.make_parent()
            self.instance = self.klass(self.parent, **self.params)
            try: cleanup = getattr(self.instance, CLEANUP_HANDLER_NAME)
            except AttributeError: pass
            else: CleanupHandler(self.parser.viewer, cleanup)
        else:
            # Asynchronous loading
            self.parent = self.make_parent()
            api = self.app.open_url(self.codeurl, 'GET', {}, self.reload)
            ModuleReader(self.context, api, self)

    def make_parent(self):
        """Creates the parent widget for the applet.

        This will be either a menu or a frame, depending on the applet's
        'menu' attribute.

        Returns:
            The parent widget.
        """
        if self.menu:
            browser = self.context.browser
            menu = AppletMenu(browser.mbar, self)
            browser.mbar.add_cascade(label=self.menu, menu=menu)
            browser.user_menus.append(menu)
            parent = menu
        else:
            text = self.viewer.text
            bg = text['background']
            frame = AppletFrame(text, self, background=bg)
            if self.width: frame.config(width=self.width)
            if self.height: frame.config(height=self.height)
            self.parser.add_subwindow(frame,
                                      hspace=self.hspace, vspace=self.vspace)
            parent = frame
        return parent                   #  FLD:  made to work in either case

    def load_it_now(self):
        """Callback for asynchronous loading.

        This method is called by the ModuleReader when the applet's code
        has been loaded.
        """
        try:
            self._load_it_now()
        except:
            self.show_tb()
        self.close()

    def _load_it_now(self):
        """Internal helper for load_it_now()."""
        mod = self.modname
        rexec = self.get_rexec()
        rexec.reset_urlpath()
        rexec.set_urlpath(self.codeurl)
        rexec.loader.load_module = self.load_module
        try:
            self.module = rexec.r_import(mod)
        finally:
            del rexec.loader.load_module
        self.parser.loaded.append(mod)
        self.klass = getattr(self.module, self.classname)
        self.instance = self.klass(self.parent, **self.params)
        try: cleanup = getattr(self.instance, CLEANUP_HANDLER_NAME)
        except AttributeError: pass
        else: CleanupHandler(self.parser.viewer, cleanup)

    def get_defaults(self):
        """Calculates default values for the applet's module name, class name,
        and code URL."""
        if self.code:                   # <APP> or <APPLET>
            if codeprog.match(self.code) >= 0:
                self.modname = codeprog.group(2)
            else:
                self.modname = "?" # Shouldn't happen
            if self.name:
                self.classname = self.name
            else:
                self.classname = self.modname
            self.codeurl = self.context.get_baseurl(
                self.codebase, self.code)
        elif self.classid or self.codebase: # <OBJECT>
            if self.classid and codeprog.match(self.classid) >= 0:
                self.codeurl = self.classid
                self.modname = codeprog.group(2)
                self.classname = self.modname
            elif self.classid:
                self.classname = self.classid
                self.modname = self.classid
                self.codeurl = self.modname + ".py"
            if self.codebase and codeprog.match(self.codebase) >= 0:
                self.modname = codeprog.group(2)
                if not self.classname:
                    self.classname = self.modname
                self.codeurl = self.context.get_baseurl(self.codebase)
            else:
                self.codeurl = self.context.get_baseurl(self.codebase,
                                                        self.codeurl)
            

    def get_easy_module(self, mod):
        """Gets a module if it can be loaded locally.

        Args:
            mod: The name of the module to get.

        Returns:
            The module object, or None if it cannot be loaded locally.
        """
        m = self.mod_is_loaded(mod)
        if not m:
            stuff = self.mod_is_local(mod)
            if stuff:
                m = self.load_module(mod, stuff)
        return m

    def mod_is_loaded(self, mod):
        """Checks if a module has already been loaded.

        Args:
            mod: The name of the module to check.

        Returns:
            The module object if it is loaded, otherwise None.
        """
        rexec = self.get_rexec()
        try:
            return rexec.modules[mod]
        except KeyError:
            return None

    def mod_is_local(self, mod):
        """Checks if a module can be found in the local search path.

        Args:
            mod: The name of the module to check.

        Returns:
            The result of `imp.find_module`, or None if the module is not
            found.
        """
        rexec = self.get_rexec()
        path = rexec.get_url_free_path()
        return rexec.loader.find_module(mod, path)

    def load_module(self, mod, stuff):
        """Loads a module from a local file.

        Args:
            mod: The name of the module to load.
            stuff: The result of `imp.find_module`.

        Returns:
            The loaded module object.

        Raises:
            ImportError: If the module type is not supported.
        """
        rexec = self.get_rexec()
        rexec.reset_urlpath()
        rexec.set_urlpath(self.codeurl)
        # XXX Duplicate stuff from rexec.RModuleLoader.load_module()
        # and even from ihooks.FancyModuleLoader.load_module().
        # This is needed to pass a copy of the source to linecace.
        file, filename, info = stuff
        (suff, mode, type) = info
        import imp
        import ihooks
        if type == imp.PKG_DIRECTORY:
            loader = self.get_rexec().loader
            return ihooks.FancyModuleLoader.load_module(loader, mod, stuff)
        if type == imp.PY_SOURCE:
            import linecache
            lines = file.readlines()
            data = string.joinfields(lines, '')
            linecache.cache[filename] = (len(data), 0, lines, filename)
            code = compile(data, filename, 'exec')
            m = rexec.hooks.add_module(mod)
            m.__file__ = filename
            m.__filename__ = filename
            exec code in m.__dict__
        elif type == imp.C_BUILTIN:
            m = imp.init_builtin(mod)
        elif type == ihooks.C_EXTENSION:
            m = rexec.load_dynamic(mod, filename, file)
        else:
            raise ImportError("Unsupported module type: %s" % repr(filename))
        return m

    def show_tb(self):
        """Displays an exception traceback in a dialog."""
        self.app.exception_dialog("during applet loading",
                                  root=self.context.root)


class ModuleReader(BaseReader):
    """Asynchronously loads an applet's source module.

    This class reads the applet's source code from a URL and then calls
    back to the AppletLoader to instantiate the applet.

    Attributes:
        apploader: The AppletLoader for the applet being loaded.
    """

    def __init__(self, context, api, apploader):
        """Initializes the ModuleReader.

        Args:
            context: The URI context.
            api: The URL API object for the applet's code.
            apploader: The AppletLoader instance.
        """
        self.apploader = apploader
        BaseReader.__init__(self, context, api)

    def handle_error(self, errno, errmsg, headers):
        """Handles an error that occurred while loading the module.

        Args:
            errno: The error number.
            errmsg: The error message.
            headers: The response headers.
        """
        self.apploader.context.error_dialog(
            ImportError,
            "Applet code at URL %s not loaded (%s: %s)" %
            (self.apploader.codeurl, errno, errmsg))
        self.apploader.close()
        self.apploader = None
        BaseReader.handle_error(self, errno, errmsg, headers)

    def handle_eof(self):
        """Callback for when the end of the file is reached."""
        apploader = self.apploader
        self.apploader = None
        apploader.load_it_now()



class Dummy:
    """A base class for dummy objects that wrap real Grail objects.

    This class provides a layer of security by exposing only a limited set of
    methods to applets.

    Attributes:
        real: The real object being wrapped.
        ok_names: A list of attribute names that are safe to access.
    """

    ok_names = []

    def __init__(self, real):
        """Initializes the Dummy object.

        Args:
            real: The real object to wrap.
        """
        self.real = real

    def __getattr__(self, name):
        """Gets an attribute, checking if it is in the allowed list."""
        if name in self.ok_names:
            attr = getattr(self.real, name)
            setattr(self, name, attr)
            return attr
        else:
            raise AttributeError(name)  # Attribute not allowed

class AppDummy(Dummy):
    """A dummy object for the Application."""
    ok_names = ['get_cache_keys']

class BrowserDummy(Dummy):
    """A dummy object for the Browser."""
    ok_names = ['load', 'message', 'valid', 'get_async_image',
                'reload_command']

    def __init__(self, real, key):
        """Initializes the BrowserDummy.

        Args:
            real: The real Browser object.
            key: The applet group key.
        """
        self.real = real
        self.key = key

    def new_command(self):
        """Creates a new browser window."""
        return BrowserBastion(self.real.new_command(), self.key)

    def clone_command(self):
        """Clones the current browser window."""
        return BrowserBastion(self.real.clone_command(), self.key)

    # 0.2 compatibility:
    
    def follow(self, url):
        """Follows a URL."""
        self.real.context.follow(url)

##    def get_async_image(self, src):
##      # For 0.2 ImageLoopItem only
##      return Bastion(self.real.get_async_image(src))

class ContextDummy(Dummy):
    """A dummy object for the URIContext."""
    ok_names = ['get_baseurl', 'load', 'follow', 'message',
                'get_async_image', 'set_local_api']

##    def get_async_image(self, src):
##      return Bastion(self.real.get_async_image(src))

class GlobalHistoryDummy(Dummy):
    """A dummy object for the GlobalHistory."""
    ok_names = ['remember_url', 'lookup_url', 'inhistory_p', 'urls']

class ParserDummy(Dummy):
    """A dummy object for the HTML parser."""
    ok_names = []

class ViewerDummy(Dummy):
    """A dummy object for the viewer."""
    ok_names = [
        'add_subwindow',
        'bind_anchors',
        # Writer methods:
        'new_alignment',
        'new_font',
        'new_margin',
        'new_spacing',
        'new_styles',
        'send_paragraph',
        'send_line_break',
        'send_hor_rule',
        'send_label_data',
        'send_flowing_data',
        'send_literal_data',
        ]

def AppBastion(real, key):
    """Creates a bastion for the Application object."""
    try:
        return real._bastions[key]
    except KeyError:
        pass
    except AttributeError:
        real._bastions = {}
    real._bastions[key] = bastion = Bastion(AppDummy(real))
    bastion.global_history = GlobalHistoryBastion(real.global_history, key)
    return bastion

def BrowserBastion(real, key):
    """Creates a bastion for the Browser object."""
    try:
        return real._bastions[key]
    except KeyError:
        pass
    except AttributeError:
        real._bastions = {}
    # Add .context instance variable to help certain applets
    real._bastions[key] = bastion = Bastion(BrowserDummy(real, key))
    bastion.context = ContextBastion(real.context, key)
    bastion.app = AppBastion(real.app, key)
    # 0.2 compatibility:
    bastion.viewer = ViewerBastion(real.context.viewer, key)
    return bastion

def ContextBastion(real, key):
    """Creates a bastion for the URIContext object."""
    try:
        return real._bastions[key]
    except KeyError:
        pass
    except AttributeError:
        real._bastions = {}
    real._bastions[key] = bastion = Bastion(ContextDummy(real))
    return bastion

def GlobalHistoryBastion(real, key):
    """Creates a bastion for the GlobalHistory object."""
    try:
        return real._bastions[key]
    except KeyError:
        pass
    except AttributeError:
        real._bastions = {}
    real._bastions[key] = bastion = Bastion(GlobalHistoryDummy(real))
    return bastion

def ParserBastion(real, key):
    """Creates a bastion for the HTML parser object."""
    try:
        return real._bastions[key]
    except KeyError:
        pass
    except AttributeError:
        real._bastions = {}
    real._bastions[key] = bastion = Bastion(ParserDummy(real))
    return bastion

def ViewerBastion(real, key):
    """Creates a bastion for the viewer object."""
    try:
        return real._bastions[key]
    except KeyError:
        pass
    except AttributeError:
        real._bastions = {}
    real._bastions[key] = bastion = Bastion(ViewerDummy(real))
    # Add the text instance variable since it is referenced by some demos.
    # Need a special filter, too!
    def filter(name):
        return name[0] != '_' or name in ('__getitem__',
                                          '__setitem__',
                                          '__str__')
    rtext = real.text
    bastion.text = btext = Bastion(real.text, filter=filter)
    btext._w = rtext._w                 # XXX This defeats the purpose :-(
    btext.tk = rtext.tk                 # XXX This too :-(
    btext.children = rtext.children     # XXX And this :-(
    btext.master = rtext.master         # XXX And so on :-(
    return bastion


class AppletMagic:
    """A mixin class that provides applets with access to Grail's core
    objects.

    This class creates bastions for the parser, viewer, context, browser, and
    app objects, providing a secure way for applets to interact with them.
    """

    def __init__(self, loader):
        """Initializes the AppletMagic.

        Args:
            loader: The AppletLoader instance.
        """
        self.grail_parser = self.grail_viewer = self.grail_context = \
                            self.grail_browser = self.grail_app = None
        if loader:
            context = loader.context
            if context:
                key = context.applet_group
                if loader.parser:
                    self.grail_parser = ParserBastion(loader.parser, key)
                if loader.viewer:
                    self.grail_viewer = ViewerBastion(loader.viewer, key)
                self.grail_context = ContextBastion(context, key)
                if context.browser:
                    self.grail_browser = BrowserBastion(context.browser, key)
                if context.app:
                    self.grail_app = AppBastion(context.app, key)


class AppletFrame(Frame, AppletMagic):
    """A Tkinter Frame that can host an applet."""

    def __init__(self, master, loader=None, cnf={}, **kw):
        """Initializes the AppletFrame.

        Args:
            master: The parent widget.
            loader: The AppletLoader instance.
            cnf: A dictionary of configuration options.
            **kw: Additional keyword arguments.
        """
        Frame.__init__(self, master, cnf, **kw)
        AppletMagic.__init__(self, loader)

    def table_geometry(self):
        """Returns the geometry for use in a table layout."""
        w = self.winfo_width()
        h = self.winfo_height()
        return w, w, h


class AppletMenu(Menu, AppletMagic):
    """A Tkinter Menu that can host an applet."""

    def __init__(self, master, loader=None, cnf={}, **kw):
        """Initializes the AppletMenu.

        Args:
            master: The parent widget.
            loader: The AppletLoader instance.
            cnf: A dictionary of configuration options.
            **kw: Additional keyword arguments.
        """
        Menu.__init__(self, master, cnf, **kw)
        AppletMagic.__init__(self, loader)


# Utilities

def get_key(context):
    """Gets the applet group key for a given context.

    Args:
        context: The URI context.

    Returns:
        The applet group key as a string.
    """
    key = _get_key(context)
    context.applet_group = key
    return key

def _get_key(context):
    """Internal helper to determine the applet group key.

    This function determines the key based on the URL and the user's
    preferences for applet groups.

    Args:
        context: The URI context.

    Returns:
        The applet group key as a string.
    """
    if context.applet_group:
        return context.applet_group
    url = context.get_url()
    app = context.app
    prefs = app.prefs
    rawgroups = prefs.Get("applets", "groups")
    groups = map(string.lower, string.split(rawgroups))
    list = []
    for group in groups:
        list.append((-len(group), string.lower(group)))
    list.sort()
    groups = []
    for length, group in list:
        groups.append(group)
    scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
    if scheme and netloc and scheme in urlparse.uses_netloc:
        netloc = string.lower(netloc)
        user, host = urllib.splituser(netloc)
        if user: return netloc          # User:passwd present -- don't mess
        netloc, port = urllib.splitport(netloc) # Port is ignored
        if netloc in groups:
            return netloc               # Exact match
        for group in groups:            # Look for longest match
            if group[:1] == '.':
                n = len(group)
                if netloc[-n:] == group:
                    return group
            if netloc == group[1:]:     # Exact match on domain name
                return group
        return netloc                   # No match, return full netloc
    return url

def get_rexec(context):
    """Gets the RExec object for a given context, if one already exists.

    Args:
        context: The URI context.

    Returns:
        The RExec object, or None if it does not exist.
    """
    app = context.app
    key = get_key(context)
    cache = app.rexec_cache
    if cache.has_key(key):
        return cache[key]

def set_reload(context):
    """Prepares the RExec object for a context for reloading.

    Args:
        context: The URI context.

    Returns:
        A ReloadHelper object.
    """
    return ReloadHelper(context)


class ReloadHelper:
    """A helper class to manage the reloading of applets.

    This class ensures that the RExec object's reload status is cleared
    once all applets have been reloaded.
    """

    def __init__(self, context):
        """Initializes the ReloadHelper.

        Args:
            context: The URI context.
        """
        self.count = 0
        self.rexec = get_rexec(context)
        if self.rexec:
            self.rexec.set_reload()

    def __del__(self):
        """Ensures that the reload status is cleared when the object is
        destroyed."""
        if self.rexec:
            self.rexec.clear_reload()
        self.rexec = None

    def attach(self, who=None):
        """Increments the reference count."""
        self.count = self.count + 1

    def detach(self, who=None):
        """Decrements the reference count and clears the reload status if
        the count reaches zero."""
        self.count = self.count - 1
        if self.count <= 0:
            if self.rexec:
                self.rexec.clear_reload()
                self.rexec = None

class CleanupHandler:
    """A helper class to run an applet's __cleanup__ method.

    This class ensures that the applet's cleanup method is called when the
    viewer is reset.
    """
    def __init__(self, viewer, handler):
        """Initializes the CleanupHandler.

        Args:
            viewer: The viewer object.
            handler: The cleanup handler function.
        """
        self._viewer = viewer
        self._handler = handler
        viewer.register_reset_interest(self)

    def __call__(self, *args):
        """Calls the cleanup handler."""
        import sys
        try: self._handler()
        except: sys.exc_traceback = None ## Pulling in show_tb from the loader
        del self._handler                ## doesn't work; not sure why.
        self._viewer.unregister_reset_interest(self)
        del self._viewer
