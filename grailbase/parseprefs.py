"""Parse a Grail preferences file.

The syntax is essentially a bunch of RFC822 message headers, but blank
lines and lines that don't conform to the "key: value" format are
ignored rather than aborting the parsing.  Continuation lines
(starting with whitespace) are honored properly.  Only keys of the
form group--component are retained (illegal keys are assumed to be
comments).  Group and component names (but not values) are converted
to lowercase before they are used.  Values are stripped of leading and
trailing whitespace; continuations are represented by an embedded
newline plus a space; otherwise, internal whitespace is left
unchanged.

The only argument is an open file, which will be read until EOF.

The return value is a dictionary of dictionaries.  The outer
dictionary represents the groups; each inner dictionary represents the
components of its group.

"""

import string
import re

validpat = r"^([-a-z0-9_]*)--([-a-z0-9_]*):(.*)$"
valid = re.compile(validpat, re.IGNORECASE)

debug = 0

def parseprefs(fp):
    """Parses a Grail preferences file.

    This function reads a preferences file, which is formatted like a series of
    RFC822 headers, and returns a nested dictionary of the preferences.

    Args:
        fp: An open file-like object to read the preferences from.

    Returns:
        A dictionary where keys are group names and values are dictionaries
        of component names to values.
    """
    groups = {}
    group = None                        # used for continuation line
    lineno = 0
    while 1:
        line = fp.readline()
        if not line:
            break
        lineno = lineno + 1
        if line[0] == '#':
            continue
        if line[0] in ' \t':
            # It looks line a continuation line.
            if group:
                # Continue the previous line
                value = line.strip()
                if value:
                    if group[cn]:
                        group[cn] = group[cn] + "\n " + value
                    else:
                        group[cn] = value
        elif valid.match(line):
            # It's a header line.
            groupname, cn, value = valid.match(line).groups()
            groupname = groupname.lower()
            cn = cn.lower()
            value = value.strip()
            if groupname not in groups:
                groups[groupname] = group = {}
            else:
                group = groups[groupname]
            group[cn] = value # XXX Override a previous value
        elif line.strip() != "":
            # It's a bad line.  Ignore it.
            if debug:
                print("Error at", lineno, ":", repr(line))

    return groups


def test():
    """Test program for parseprefs().

    This function takes a filename as a command line argument, parses it,
    and prints the results. If no filename is given, it defaults to
    '../data/grail-defaults'. It also times the parsing process.
    """
    import sys
    import time
    global debug
    debug = 1
    if sys.argv[1:]:
        fn = sys.argv[1]
    else:
        fn = "../data/grail-defaults"
    fp = open(fn)
    t0 = time.time()
    groups = parseprefs(fp)
    t1 = time.time()
    fp.close()
    print("Parsing time", round(t1-t0, 3))
    groupnames = list(groups.keys())
    groupnames.sort()
    for groupname in groupnames:
        print()
        print(groupname)
        print('=' * len(groupname))
        print()
        group = groups[groupname]
        componentnames = list(group.keys())
        componentnames.sort()
        for cn in componentnames:
            value = group[cn]
            print(cn + ":", repr(value))


if __name__ == '__main__':
    test()
