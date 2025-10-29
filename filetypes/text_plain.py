"""Grail parser for text/plain."""
__version__ = '$Revision: 2.8 $'

import formatter
import grailutil
import Reader
import string


def parse_text_plain(*args, **kw):
    """Parses a text/plain document.

    This function checks the Content-Type header for a 'format' parameter.
    If the format is 'flowed', it uses the FlowingTextParser. Otherwise, it
    uses the standard TextParser.

    Args:
        *args: Variable length argument list.
        **kw: Arbitrary keyword arguments.

    Returns:
        An instance of the appropriate parser.
    """
    headers = args[0].context.get_headers()
    ctype = headers.get('content-type')
    if ctype:
        ctype, opts = grailutil.conv_mimetype(ctype)
        if opts.get('format'):
            how = opts['format'].lower()
            if how == "flowed":
                import FlowingText
                return FlowingText.FlowingTextParser(*args, **kw)
    return Reader.TextParser(*args, **kw)
