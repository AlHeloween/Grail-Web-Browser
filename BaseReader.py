"""Base reader class -- read from a URL in the background."""

import sys
import string
from Tkinter import *
import urlparse
import grailutil


# Default tuning parameters
# BUFSIZE = 8*1024                      # Buffer size for api.getdata()
BUFSIZE = 512                           # Smaller size for better response
SLEEPTIME = 100                         # Milliseconds between regular checks

class BaseReader:
    """A base class for asynchronously reading data from a URL.

    This class provides the core functionality for polling a URL API object,
    reading data in the background, and reporting status updates.

    Attributes:
        context: The URI context.
        api: The URL API object.
        callback: The current callback function.
        poller: The current poller function.
        bufsize: The buffer size for reading data.
        nbytes: The number of bytes read so far.
        maxbytes: The total number of bytes to read.
        shorturl: A shortened version of the URL for display.
        message: A status message.
        fno: The file number of the socket.
        killed: A flag indicating whether the reader has been killed.
    """

    # Tuning parameters
    sleeptime = SLEEPTIME

    def __init__(self, context, api):
        """Initializes the BaseReader.

        Args:
            context: The URI context.
            api: The URL API object.
        """
        self.context = context
        self.api = api
        self.callback = self.checkmeta
        self.poller = self.api.pollmeta
        self.bufsize = BUFSIZE
        
        # Stuff for status reporting
        self.nbytes = 0
        self.maxbytes = 0
        self.shorturl = ""
        self.message = "waiting for socket"

        self.context.addreader(self)

        self.fno = None   # will be assigned by start
        self.killed = None

        # Only http_access has delayed startup property.
        # Second argument would allow implementation of persistent
        # connections.
        try:
            self.api.register_reader(self.start, self.checkapi)
        except AttributeError:
            # if the protocol doesn't do that
            ok = 0
            try:
                self.start()
                ok = 1
            finally:
                if not ok:
                    if self.context:
                        self.context.rmreader(self)

    def start(self):
        """Starts the reading process.

        This method sets up a file handler or a timer to poll for data.
        """
        # when the protocol API is ready to go, it tells the reader
        # to get busy
        self.message = "awaiting server response"
        if self.killed:
            print "start() called after a kill"
            return
        self.fno = self.api.fileno()
        if TkVersion == 4.0 and sys.platform == 'irix5':
            if self.fno >= 20: self.fno = -1 # XXX for SGI Tk OPEN_MAX bug

        if self.fno >= 0:
            tkinter.createfilehandler(
                self.fno, tkinter.READABLE, self.checkapi)
        else:
            # No fileno() -- check every 100 ms
            self.checkapi_regularly()

        # Delete pervious context local protocol handlers
        # We've gotten far enough into the next page without errors
        if self.context:
            self.context.remove_local_api_handlers()

    def __str__(self):
        if self.maxbytes:
            percent = self.nbytes*100/self.maxbytes
            status = "%d%% of %s read" % (percent,
                                          grailutil.nicebytes(self.maxbytes))
        elif not self.nbytes:
            status = self.message
        else:
            status = "%s read" % grailutil.nicebytes(self.nbytes)
        if self.api and self.api.iscached():
            status = status + " (cached)"
        if self.api and not self.shorturl:
            tuple = urlparse.urlparse(self.api._url_)
            path = tuple[2]
            i = string.rfind(path[:-1], '/')
            if i >= 0:
                path = path[i+1:]
            self.shorturl = path or self.api._url_
        return "%s: %s" % (self.shorturl, status)

    def __repr__(self):
        return "%s(...%s)" % (self.__class__.__name__, self.api)

    def update_status(self):
        """Updates the status display for this reader."""
        self.context.new_reader_status() # Will call our __str__() method

    def update_maxbytes(self, headers):
        """Updates the total number of bytes to be read.

        Args:
            headers: A dictionary of response headers.
        """
        self.maxbytes = 0
        if headers.has_key('content-length'):
            try:
                self.maxbytes = string.atoi(headers['content-length'])
            except string.atoi_error:
                pass
        self.update_status()

    def update_nbytes(self, data):
        """Updates the number of bytes read so far.

        Args:
            data: The chunk of data that was just read.
        """
        self.nbytes = self.nbytes + len(data)
        self.update_status()

    def kill(self):
        """Stops the reader and reports an error."""
        self.killed = 1
        self.stop()
        self.handle_error(-1, "Killed", {})

    def stop(self):
        """Stops the reader and cleans up resources."""
        if self.fno >= 0:
            fno = self.fno
            self.fno = -1
            tkinter.deletefilehandler(fno)

        self.callback = None
        self.poller = None

        if self.api:
            self.api.close()
            self.api = None

        if self.context:
            self.context.rmreader(self)
            self.context = None

    def checkapi_regularly(self):
        """Periodically checks the API for data, for use when a file
        descriptor is not available."""
        if not self.callback:
##          print "*** checkapi_regularly -- too late ***"
            return
        self.callback()
        if self.callback:
            sleeptime = self.sleeptime
            if self.poller and self.poller()[1]: sleeptime = 0
            self.context.root.after(sleeptime, self.checkapi_regularly)

    def checkapi(self, *args):
        """Callback for the file handler. This calls the current callback
        function."""
        if not self.callback:
            print "*** checkapi -- too late ***"
            if self.fno >= 0:
                fno = self.fno
                self.fno = -1
                tkinter.deletefilehandler(fno)
            return
        try:
            self.callback()                     # Call via function pointer
        except:
            if self.context and self.context.app:
                app = self.context.app
            else:
                app = grailutil.get_grailapp()
            app.exception_dialog("in BaseReader")
            self.kill()

    def checkmeta(self):
        """Checks for metadata from the URL."""
        self.message, ready = self.api.pollmeta()
        if ready:
            self.getapimeta()

    def checkdata(self):
        """Checks for data from the URL."""
        self.message, ready = self.api.polldata()
        if ready:
            self.getapidata()

    def getapimeta(self):
        """Gets metadata from the URL and calls the meta handler."""
        errcode, errmsg, headers = self.api.getmeta()
        self.callback = self.checkdata
        self.poller = self.api.polldata
        if headers.has_key('content-type'):
            content_type = headers['content-type']
        else:
            content_type = None
        if headers.has_key('content-encoding'):
            content_encoding = headers['content-encoding']
        else:
            content_encoding = None
        self.content_type = content_type
        self.content_encoding = content_encoding
        self.update_maxbytes(headers)
        self.handle_meta(errcode, errmsg, headers)
        if self.callback:
            self.callback()             # XXX Handle httpAPI readahead

    def getapidata(self):
        """Gets data from the URL and calls the data handler."""
        data = self.api.getdata(self.bufsize)
        if not data:
            self.handle_eof()
            self.stop()
            return
        self.update_nbytes(data)
        self.handle_data(data)

    def geteverything(self):
        """Reads all data from the URL synchronously."""
        if self.api:
            if self.callback == self.checkmeta:
                self.getapimeta()
            while self.api:
                self.getapidata()

    # Derived classes are expected to override the following methods

    def handle_meta(self, errcode, errmsg, headers):
        """Handles the metadata from the URL.

        This method is intended to be overridden by subclasses.
        """
        # May call self.stop()
        self.update_maxbytes(headers)
        if errcode != 200:
            self.stop()
            self.handle_error(errcode, errmsg, headers)

    def handle_data(self, data):
        """Handles a chunk of data from the URL.

        This method is intended to be overridden by subclasses.
        """
        # May call self.stop()
        pass

    def handle_error(self, errcode, errmsg, headers):
        """Handles an error that occurred while reading from the URL.

        This method is intended to be overridden by subclasses.
        """
        # Called after self.stop() has been called
        pass

    def handle_eof(self):
        """Handles the end of the data stream.

        This method is intended to be overridden by subclasses.
        """
        # Called after self.stop() has been called
        pass
