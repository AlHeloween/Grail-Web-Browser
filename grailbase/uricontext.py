"""URI resolution context.

The use of 'url' in the method names is a historical accident.

"""
__version__ = '$Revision: 1.5 $'

from urllib import parse as urlparse
__default_joiner = urlparse.urljoin
del urlparse

import re
__typematch = re.compile('^([^/:]+):').match
del re

def __splittype(url):
    match = __typematch(url)
    if match:
        return match.group(1)


def _urljoin(a, b):
    sa = __splittype(a)
    sb = __splittype(b)
    if sa and (sa == sb or not sb):
        import protocols
        joiner = protocols.protocol_joiner(sa)
        if joiner: return joiner(a, b)
    return __default_joiner(a, b)


class URIContext:
    """Manages the context for resolving URIs.

    This class keeps track of the current URL and a base URL for resolving
    relative links.

    Attributes:
        __url: The current URL.
        __baseurl: The base URL for resolving relative links.
    """

    def __init__(self, url="", baseurl=""):
        """Initializes the URIContext.

        Args:
            url: The initial URL.
            baseurl: The initial base URL.
        """
        self.__url = url or ""
        baseurl = baseurl or ""
        if url and baseurl:
            self.__baseurl = _urljoin(url, baseurl)
        else:
            self.__baseurl = baseurl

    def get_url(self):
        """Gets the current URL.

        Returns:
            The current URL as a string.
        """
        return self.__url

    def set_url(self, url, baseurl=None):
        """Sets the source URI and base URI for the current resource.

        The loaded URI is what this page was loaded from; the base URI
        is used to calculate relative links, and defaults to the
        loaded URI.

        Args:
            url: The new current URL.
            baseurl: An optional new base URL. If not provided, the base URL
                is set to the new current URL.
        """
        self.__url = url
        if baseurl:
            self.__baseurl = _urljoin(url, baseurl)
        else:
            self.__baseurl = url

    def get_baseurl(self, *relurls):
        """Returns the base URI, optionally joined with relative URIs.

        Without arguments, this method returns the current base URI. With
        arguments, it returns the base URI joined with each of the relative
        URIs.

        Args:
            *relurls: A variable number of relative URLs to join with the base
                URI.

        Returns:
            The resulting URL as a string.
        """
        
        url = self.__baseurl or self.__url
        for rel in relurls:
            if rel:
                url = _urljoin(url, rel)
        return url

    def set_baseurl(self, baseurl):
        """Sets the base URI for the current page.

        The new base URI is resolved relative to the existing base URI.

        Args:
            baseurl: The new base URL.
        """
        if baseurl:
            self.__baseurl = _urljoin(self.__baseurl or self.__url, baseurl)
        else:
            self.__baseurl = self.__baseurl or self.__url
