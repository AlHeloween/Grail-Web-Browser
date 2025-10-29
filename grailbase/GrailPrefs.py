"""Functional interface to Grail user preferences.

See the Grail htdocs/info/extending/preferences.html for documentation."""

# To test, "(cd <scriptdir>; python GrailPrefs.py)".

__version__ = "$Revision: 2.33 $"

import os
import sys
import string
if __name__ == "__main__":
    sys.path.insert(0, '../utils')
import utils

import parseprefs

USERPREFSFILENAME = 'grail-preferences'
SYSPREFSFILENAME = os.path.join('data', 'grail-defaults')

verbose = 0

class Preferences:
    """Manages reading and writing of a single preferences file.

    This class handles a single preferences file, tracking saved settings,
    modifications, and deletions. It provides methods for getting, setting,
    and deleting preferences, as well as for saving the changes back to the
    file.

    Attributes:
        filename: The path to the preferences file.
        mods: A dictionary of modified preferences that have not yet been
            saved.
        deleted: A dictionary of preferences that have been deleted.
        saved: A dictionary of the preferences as last read from the file.
        last_mtime: The last modification time of the file.
        modified: A flag indicating whether the preferences have been modified.
    """

    def __init__(self, filename, readonly=0):
        """Initializes the Preferences object.

        Args:
            filename: The path to the preferences file.
            readonly: A flag indicating whether the file should be treated as
                read-only.
        """
        self.filename = filename
        self.mods = {}                  # Changed settings not yet saved.
        self.deleted = {}               # Settings overridden, not yet saved.
        try:
            f = open(filename)
            self.last_mtime = os.stat(filename)[9]
            self.saved = parseprefs.parseprefs(f)
            f.close()
        except IOError:
            self.saved = {}
            self.last_mtime = 0
        self.modified = 0

    def Get(self, group, cmpnt):
        """Gets a preference value.

        Checks for the preference in modified, then saved preferences.

        Args:
            group: The preference group.
            cmpnt: The preference component.

        Returns:
            The value of the preference.

        Raises:
            KeyError: If the preference is not found.
        """
        if group in self.mods and cmpnt in self.mods[group]:
            return self.mods[group][cmpnt]
        elif group in self.saved and cmpnt in self.saved[group]:
            return self.saved[group][cmpnt]
        else:
            raise KeyError("Preference %s not found" % ((group, cmpnt),))

    def Set(self, group, cmpnt, val):
        """Sets a preference value.

        The value is stored in the `mods` dictionary until saved.

        Args:
            group: The preference group.
            cmpnt: The preference component.
            val: The new value for the preference.
        """
        self.modified = 1
        if group not in self.mods:
            self.mods[group] = {}
        self.mods[group][cmpnt] = str(val)
        if group in self.deleted and cmpnt in self.deleted[group]:
            # Undelete.
            del self.deleted[group][cmpnt]

    def __delitem__(self, key):
        """Marks a preference for deletion.

        The preference is added to the `deleted` dictionary and will be
        removed from the saved preferences when the file is saved.

        Args:
            key: A tuple of (group, component).
        """
        group, cmpnt = key
        self.Get(group, cmpnt)  # Verify item existence.
        if group not in self.deleted:
            self.deleted[group] = {}
        self.deleted[group][cmpnt] = 1

    def items(self):
        """Returns a list of all preferences.

        This method consolidates saved and modified preferences, with
        modifications taking precedence. Deleted preferences are excluded.

        Returns:
            A list of ((group, component), value) tuples.
        """
        got = {}
        deleted = self.deleted
        # Consolidate established and changed, with changed having precedence:
        for g, comps in list(self.saved.items()) + list(self.mods.items()):
            for c, v in comps.items():
                if not (g in deleted and c in deleted[g]):
                    got[(g,c)] = v
        return got.items()

    def Tampered(self):
        """Checks if the preferences file has been modified externally.

        Returns:
            True if the file has been modified since it was last read,
            False otherwise.
        """
        return os.stat(self.filename)[9] != self.mtime

    def Editable(self):
        """Checks if the preferences file is editable.

        This method will also attempt to create the user's grail directory
        and the preferences file if they do not exist.

        Returns:
            True if the file is editable, False otherwise.
        """
        if not utils.establish_dir(os.path.split(self.filename)[0]):
            return 0
        elif os.path.exists(self.filename):
            return 1
        else:
            try:
                tempf = open(self.filename, 'a')
                tempf.close()
                return 1
            except os.error:
                return 0

    def Save(self):
        """Saves the preferences to the file.

        This method writes all modified preferences to the file, after
        creating a backup of the original file.
        """
        try: os.rename(self.filename, self.filename + '.bak')
        except os.error: pass           # No file to backup.

        fp = open(self.filename, 'w')
        items = self.items()
        items.sort()
        prevgroup = None
        for (g, c), v in items:
            if prevgroup and g != prevgroup:
                fp.write('\n')
            fp.write(make_key(g, c) + ': ' + v + '\n')
            prevgroup = g
        fp.close()
        # Register that modifications are now saved:
        deleted = self.deleted
        for g, comps in self.mods.items():
            for c, v in comps.items():
                if not (g in deleted and c in deleted[g]):
                    if g not in self.saved:
                        self.saved[g] = {}
                    self.saved[g][c] = v
                elif g in self.saved and c in self.saved[g]:
                    # Deleted - remove from saved version:
                    del self.saved[g][c]
        # ... and reinit mods and deleted records:
        self.mods = {}
        self.deleted = {}

class AllPreferences:
    """Manages the combination of user and system preferences.

    This class provides a unified view of preferences from both the user's
    preferences file and the system-wide defaults. It handles loading,
    getting, setting, and saving preferences, as well as managing callbacks
    for preference changes.

    Attributes:
        user: A Preferences object for the user's preferences file.
        sys: A Preferences object for the system's preferences file.
        callbacks: A dictionary of callbacks to be invoked when preferences
            are changed.
    """
    def __init__(self):
        """Initializes the AllPreferences object."""
        self.load()
        self.callbacks = {}

    def load(self):
        """Loads both user and system preferences from their respective files."""
        self.user = Preferences(os.path.join(utils.getgraildir(),
                                             USERPREFSFILENAME))
        self.sys = Preferences(os.path.join(utils.get_grailroot(),
                                            SYSPREFSFILENAME),
                               1)

    def AddGroupCallback(self, group, callback):
        """Registers a callback to be invoked when preferences in a group are
        changed.

        Each callback will be invoked only once per concerned group per
        save (even if multiply registered for that group), and callbacks
        within a group will be invoked in the order they were registered.

        Args:
            group: The preference group to monitor.
            callback: The function to call when the group's preferences
                change.
        """
        if group in self.callbacks:
            if callback not in self.callbacks[group]:
                self.callbacks[group].append(callback)
        else:
            self.callbacks[group] = [callback]

    def RemoveGroupCallback(self, group, callback):
        """Removes a registered group-prefs callback func.

        Silently ignores unregistered callbacks.

        Args:
            group: The preference group.
            callback: The callback function to remove.
        """
        try:
            self.callbacks[group].remove(callback)
        except (ValueError, KeyError):
            pass

    # Getting:

    def Get(self, group, cmpnt, factory=0):
        """Gets a preference value, trying user preferences first, then system
        defaults.

        Args:
            group: The preference group.
            cmpnt: The preference component.
            factory: If True, gets the system default ("factory") value
                directly.

        Returns:
            The value of the preference.

        Raises:
            KeyError: If the preference is not found.
        """
        if factory:
            return self.sys.Get(group, cmpnt)
        else:
            try:
                return self.user.Get(group, cmpnt)
            except KeyError:
                return self.sys.Get(group, cmpnt)

    def GetTyped(self, group, cmpnt, type_name, factory=0):
        """Gets a preference and converts it to a specific type.

        Args:
            group: The preference group.
            cmpnt: The preference component.
            type_name: The name of the type to convert to (e.g., 'int',
                'float', 'Boolean').
            factory: If True, gets the system default value.

        Returns:
            The typed value of the preference.

        Raises:
            KeyError: If the preference is not found.
            TypeError: If the value cannot be converted to the specified type.
        """
        val = self.Get(group, cmpnt, factory)
        try:
            return typify(val, type_name)
        except TypeError:
            raise TypeError('%s should be %s: %s'
                               % (str((group, cmpnt)), type_name, repr(val)))

    def GetInt(self, group, cmpnt, factory=0):
        """Gets an integer preference."""
        return self.GetTyped(group, cmpnt, "int", factory)
    def GetFloat(self, group, cmpnt, factory=0):
        """Gets a float preference."""
        return self.GetTyped(group, cmpnt, "float", factory)
    def GetBoolean(self, group, cmpnt, factory=0):
        """Gets a Boolean preference."""
        return self.GetTyped(group, cmpnt, "Boolean", factory)

    def GetGroup(self, group):
        """Gets all preferences in a given group.

        Args:
            group: The name of the group.

        Returns:
            A list of ((group, component), value) tuples for the specified
            group.
        """
        got = []
        prefix = group.lower() + '--'
        l = len(prefix)
        for it in self.items():
            if it[0][0] == group:
                got.append(it)
        return got

    def items(self):
        """Returns a list of all preferences, combining user and system
        settings.

        User settings override system settings.

        Returns:
            A list of ((group, component), value) tuples.
        """
        got = {}
        for it in self.sys.items():
            got[it[0]] = it[1]
        for it in self.user.items():
            got[it[0]] = it[1]
        return got.items()

    # Editing:

    def Set(self, group, cmpnt, val):
        """Sets a preference value in the user's preferences.

        Args:
            group: The preference group.
            cmpnt: The preference component.
            val: The new value.
        """
        if self.Get(group, cmpnt) != val:
            self.user.Set(group, cmpnt, val)

    def Editable(self):
        """Checks if the user's preferences file is editable.

        Returns:
            True if the file is editable, False otherwise.
        """
        return self.user.Editable()

    def Tampered(self):
        """Checks if the user's preferences file has been modified externally.

        Returns:
            True if the file has been tampered with, False otherwise.
        """
        return self.user.Tampered()

    def Save(self):
        """Saves the user's preferences to their file.

        This method will only save values that are different from the system
        defaults. After saving, it will invoke any registered callbacks for
        the modified preference groups.
        """
        # Callbacks are processed after the save.

        # Identify the pending callbacks before user-prefs culling:
        pending_groups = self.user.mods.keys()

        # Cull the user items to remove any settings that are identical to
        # the ones in the system defaults:
        for (g, c), v in self.user.items():
            try:
                if self.sys.Get(g, c) == v:
                    del self.user[(g, c)]
            except KeyError:
                # User file pref absent from system file - may be for
                # different version, so leave it be:
                continue

        try:
            self.user.Save()
        except IOError:
            print("Failed save of user prefs.")

        # Process the callbacks:
        callbacks, did_callbacks = self.callbacks, {}
        for group in pending_groups:
            if group in self.callbacks:
                for callback in callbacks[group]:
                    # Ensure each callback is invoked only once per save,
                    # in order:
                    if callback not in did_callbacks:
                        did_callbacks[callback] = 1
                        callback()

def make_key(group, cmpnt):
    """Creates a preference key string from a group and component.

    Args:
        group: The preference group.
        cmpnt: The preference component.

    Returns:
        A string in the format "group--component".
    """
    return string.lower(group + '--' + cmpnt)
                    

def typify(val, type_name):
    """Converts a string value to a specified type.

    Args:
        val: The string value to convert.
        type_name: The name of the type to convert to ('string', 'int',
            'float', or 'Boolean').

    Returns:
        The converted value.

    Raises:
        TypeError: If the value cannot be converted to the specified type.
        ValueError: If the type_name is not supported.
    """
    try:
        if type_name == 'string':
            return val
        elif type_name == 'int':
            return int(val)
        elif type_name == 'float':
            return float(val)
        elif type_name == 'Boolean':
            i = int(val)
            if i not in (0, 1):
                raise TypeError('%s should be Boolean' % repr(val))
            return i
    except ValueError:
            raise TypeError('%s should be %s' % (repr(val), type_name))
    
    raise ValueError('%s not supported - must be one of %s'
                       % (repr(type_name), ['string', 'int', 'float', 'Boolean']))
    

def test():
    """Exercises the preferences mechanisms.

    This function tests reading, setting, and saving preferences. It
    modifies and then restores a setting in the user's preferences file.
    """
    sys.path.insert(0, "../utils")
    from testing import exercise
    
    env = sys.modules[__name__].__dict__

    # Reading the db:
    exercise("prefs = AllPreferences()", env, "Suck in the prefs")

    # Getting values:
    exercise("origin = prefs.Get('landmarks', 'grail-home-page')", env,
             "Get an existing plain component.")
    exercise("origheight = prefs.GetInt('browser', 'default-height')", env,
             "Get an existing int component.")
    exercise("if prefs.GetBoolean('browser', 'load-images') != 1:"
             + "raise SystemError, 'browser:load-images Boolean should be 1'",
             env, "Get an existing Boolean component.")
    # A few value errors:
    exercise("x = prefs.Get('grail', 'Never:no:way:no:how!')", env,
             "Ref to a non-existent component.", KeyError)
    exercise("x = prefs.GetInt('landmarks', 'grail-home-page')", env,
             "Typed ref to incorrect type.", TypeError)
    exercise("x = prefs.GetBoolean('browser', 'default-height')", env,
             "Invalid Boolean (which has complicated err handling) typed ref.",
             TypeError)
    # Editing:
    exercise("prefs.Set('browser', 'default-height', origheight + 1)", env,
             "Set a simple value")
    exercise("if prefs.GetInt('browser', 'default-height') != origheight + 1:"
             + "raise SystemError, 'Set of new height failed'", env,
             "Get the new value.")
    prefs.Save()

    exercise("prefs.Set('browser', 'default-height', origheight)", env,
             "Restore simple value")

    # Saving - should just rewrite existing user prefs file, sans comments
    # and any lines duplicating system prefs.
    exercise("prefs.Save()", env, "Save as it was originally.")
    

    print("GrailPrefs tests passed.")
    return prefs

if __name__ == "__main__":

    global grail_root
    grail_root = '..'

    prefs = test()
