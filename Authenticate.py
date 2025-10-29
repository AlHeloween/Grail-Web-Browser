"""Framework for allowing flexible access authorization.

To start, this is used by the HTTP api to perform basic access authorization.
"""

from Tkinter import *
import tktools
import string
import urlparse
import base64
import regex

class AuthenticationManager:
    """Handles HTTP access authorization.

    This class manages authentication credentials for different realms and
    provides a mechanism for requesting credentials from the user when
    required.

    Attributes:
        app: The main application object.
        basic_realms: A dictionary to store credentials for basic access
            authorization.
    """

    def __init__(self, app):
        """Initializes the AuthenticationManager.

        Args:
            app: The main application object.
        """
        self.app = app

        # initialize 'basic' storage
        self.basic_realms = {}

    def request_credentials(self, headers):
        """Requests authentication credentials.

        This method determines the authentication scheme from the response
        headers and then attempts to retrieve the appropriate credentials.

        Args:
            headers: A dictionary of headers from the 401 response.

        Returns:
            A dictionary of headers to be included in the next request, or an
            empty dictionary if credentials cannot be obtained.
        """
        # response isa {}

        # first guess the scheme
        if 'www-authenticate' in headers:
            # assume it's basic
            headers['realm'] = \
                             self.basic_get_realm(headers['www-authenticate'])
            response = self.basic_credentials(headers)
        else:
            # don't know the scheme
            response = {}

        return response

    def invalidate_credentials(self, headers, credentials):
        """Invalidates a set of credentials.

        Args:
            headers: A dictionary of headers from the 401 response.
            credentials: The credentials to invalidate.
        """
        if 'www-authenticate' in headers:
            # assume it's basic
            headers['realm'] = \
                             self.basic_get_realm(headers['www-authenticate'])
            self.basic_invalidate_credentials(headers, credentials)
        else:
            # don't know about anything other than basic
            pass

    basic_realm = regex.compile('realm="\(.*\)"')

    def basic_get_realm(self,challenge):
        """Extracts the realm from a 'www-authenticate' header.

        Args:
            challenge: The value of the 'www-authenticate' header.

        Returns:
            The realm string, or None if it cannot be found.
        """
        # the actual specification allows for multiple name=value
        # entries seperated by commes, but for basic they don't
        # have any defined value. so don't bother with them.
        if self.basic_realm.search(challenge) < 0:
            return
        realm = self.basic_realm.group(1)
        return realm

    def basic_credentials(self, data):
        """Gets credentials for basic access authorization.

        This method will either retrieve cached credentials or prompt the
        user for them.

        Args:
            data: A dictionary of data from the 401 response, including
                'realm' and 'request-uri'.

        Returns:
            A dictionary containing the 'Authorization' header, or an empty
            dictionary if credentials cannot be obtained.
        """
        response = {}

        if 'realm' in data and 'request-uri' in data:
            scheme, netloc, path, nil, nil, nil = \
                    urlparse.urlparse(data['request-uri'])
            key = (netloc, data['realm'])
            if key in self.basic_realms:
                cookie = self.basic_cookie(self.basic_realms[key])
            else:
                passwd = self.basic_user_dialog(data)
                if passwd:
                    self.basic_realms[key] = passwd
                    cookie = self.basic_cookie(passwd)
                else:
                    return {}
            response['Authorization'] = cookie

        return response

    def basic_invalidate_credentials(self, headers, credentials):
        """Invalidates a set of basic credentials.

        Args:
            headers: A dictionary of headers from the 401 response.
            credentials: The credentials to invalidate.
        """
        if 'realm' in headers and 'request-uri' in headers:
            scheme, netloc, path, nil, nil, nil = \
                    urlparse.urlparse(headers['request-uri'])
            key = (netloc, headers['realm'])
            if key in self.basic_realms:
                test = self.basic_cookie(self.basic_realms[key])
                if test == credentials:
                    del self.basic_realms[key]

    def basic_snoop(self, headers):
        """Snoops on requests to learn about protection spaces."""
        # could watch other requests go by and learn about protection spaces
        pass

    def basic_cookie(self, str):
        """Creates a 'Basic' authorization cookie.

        Args:
            str: The 'username:password' string.

        Returns:
            The 'Authorization' header value.
        """
        return "Basic " + string.strip(base64.encodestring(str))

    def basic_user_dialog(self, data):
        """Displays a dialog to get username and password from the user.

        Args:
            data: A dictionary of data from the 401 response.

        Returns:
            The 'username:password' string, or None if the user cancels.
        """
        scheme, netloc, path, \
                nil, nil, nil = urlparse.urlparse(data['request-uri'])
        login = LoginDialog(self.app.root, netloc,
                            data['realm'])
        return login.go()
    
    def more_complete_challenge_parse(self):
        # this is Guido's old code from Reader.handle_auth_error
        # it's worth hanging on to in case a future authentication
        # scheme uses more than one field in the challenge
        return

        challenge = headers['www-authenticate']
        # <authscheme> realm="<value>" [, <param>="<value>"] ...
        parts = string.splitfields(challenge, ',')
        p = parts[0]
        i = string.find(p, '=')
        if i < 0: return
        key, value = p[:i], p[i+1:]
        keyparts = string.split(string.lower(key))
        if not(len(keyparts) == 2 and keyparts[1] == 'realm'): return
        authscheme = keyparts[0]
        value = string.strip(value)
        if len(value) >= 2 and value[0] == value[-1] and value[0] in '\'"':
            value = value[1:-1]


class LoginDialog:
    """A dialog for getting username and password from the user.

    Attributes:
        root: The root Tkinter window for the dialog.
        prompt: The label displaying the prompt.
        user_entry: The entry for the username.
        passwd_entry: The entry for the password.
        ok_button: The OK button.
        cancel_button: The Cancel button.
        user_passwd: The 'username:password' string, or None if canceled.
    """

    def __init__(self, master, netloc, realmvalue):
        """Initializes the LoginDialog.

        Args:
            master: The parent window.
            netloc: The network location (hostname:port).
            realmvalue: The authentication realm.
        """
        self.root = tktools.make_toplevel(master,
                                          title="Authentication Dialog")
        self.prompt = Label(self.root,
                            text="Enter user authentication\nfor %s on %s" %
                            (realmvalue, netloc))
        self.prompt.pack(side=TOP)
        self.user_entry, dummy = tktools.make_form_entry(self.root, "User:")
        self.user_entry.focus_set()
        self.user_entry.bind('<Return>', self.user_return_event)
        self.passwd_entry, dummy = \
                           tktools.make_form_entry(self.root, "Password:")
        self.passwd_entry.config(show="*")
        self.passwd_entry.bind('<Return>', self.ok_command)
        self.ok_button = Button(self.root, text="OK", command=self.ok_command)
        self.ok_button.pack(side=LEFT)
        self.cancel_button = Button(self.root, text="Cancel",
                                    command=self.cancel_command)
        self.cancel_button.pack(side=RIGHT)

        self.user_passwd = None

        tktools.set_transient(self.root, master)

        self.root.grab_set()

    def go(self):
        """Displays the dialog and waits for the user to enter credentials.

        Returns:
            The 'username:password' string, or None if the user cancels.
        """
        try:
            self.root.mainloop()
        except SystemExit:
            return self.user_passwd

    def user_return_event(self, event):
        """Event handler for the Return key in the user entry."""
        self.passwd_entry.focus_set()

    def ok_command(self, event=None):
        """Event handler for the OK button."""
        user = string.strip(self.user_entry.get())
        passwd = string.strip(self.passwd_entry.get())
        if not user:
            self.root.bell()
            return
        self.user_passwd = user + ':' + passwd
        self.goaway()

    def cancel_command(self):
        """Event handler for the Cancel button."""
        self.user_passwd = None
        self.goaway()

    def goaway(self):
        """Closes the dialog."""
        self.root.destroy()
        raise SystemExit

