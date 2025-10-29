"""image/gif document handling for Grail.

This supports both plain Tk support and PIL-enhanced support.  When PIL is
available and the line

        browser--enable-pil: 1

is located in the ~/.grail/grail-preferences file, PIL will be used and can
support animation of GIF89a files as well as single-frame display.  We still
need a way for the user to STOP the animation!

The files Grail/*.py from the PIL distribution should be installed in the
same directory as this file.
"""
import AsyncImage
import grailutil
import os
import string
import sys
import tempfile
import Tkinter

from formatter import AS_IS

try:
    from io import StringIO
except ImportError:
    from io import StringIO


ERROR_FILE = os.path.join("icons", "sadsmiley.gif")


class pil_interface:
    """Dummy class to keep us from having to define PILGifParser within a
    try/except construct."""
    pass

try:
    import Image
    import ImageTk
    from pil_interface import pil_interface
except ImportError:
    _use_pil = 0
else:
    _use_pil = 1


class PILGifParser(pil_interface):
    """A parser for GIF images using the Python Imaging Library (PIL).

    This class handles both static and animated GIFs.

    Attributes:
        im: The PIL Image object.
        currentpos: The current frame number for animated GIFs.
        duration: The duration of the current frame in milliseconds.
        loop: The number of times to loop an animated GIF.
    """
    im = None
    currentpos = 0
    duration = 0
    loop = 0

    def close(self):
        """Finalizes the parsing process.

        This method decodes the image data and displays the first frame. If the
        image is an animated GIF, it starts the animation loop.
        """
        if self.buf:
            self.label.config(text="<decoding>")
            self.label.update_idletasks()
            data = "".join(self.buf)
            self.buf = None             # free lots of memory!
            try:
                self.im = im = Image.open(StringIO(data))
                im.load()
                self.tkim = tkim = ImageTk.PhotoImage(im.mode, im.size)
                tkim.paste(im)
            except:
                # XXX What was I trying to catch here?
                # I think (EOFError, IOError).
                self.broken = 1
                stdout = sys.stdout
                try:
                    sys.stdout = sys.stderr
                    import traceback
                    traceback.print_exc()
                finally:
                    sys.stdout = stdout
            else:
                self.label.config(image=tkim)
                if "duration" in im.info:
                    self.duration = im.info["duration"]
                if "loop" in im.info:
                    self.duration = self.duration or 100
                    self.loop = im.info["loop"]
                    self.data = data
                if self.duration or self.loop:
                    self.viewer.register_reset_interest(self.cancel_loop)
                    self.after_id = self.label.after(self.duration,
                                                     self.next_image)
        if self.broken:
            self.label.image = Tkinter.PhotoImage(
                file=grailutil.which(ERROR_FILE))
            self.label.config(image = self.label.image)
            self.viewer.text.insert(Tkinter.END, '\nBroken Image!')

    def next_image(self):
        """Displays the next frame of an animated GIF."""
        newpos = self.currentpos + 1
        try:
            self.im.seek(newpos)
        except (ValueError, EOFError):
            # past end of animation
            if self.loop:
                self.reset_loop()
            else:
                # all done
                self.viewer.unregister_reset_interest(self.cancel_loop)
                return
        else:
            self.currentpos = newpos
            self.tkim.paste(self.im)
        self.after_id = self.label.after(self.duration, self.next_image)

    def reset_loop(self):
        """Resets an animated GIF to the first frame."""
        im = Image.open(StringIO(self.data))
        im.load()
        self.tkim.paste(im)
        self.im = im
        self.currentpos = 0

    def cancel_loop(self, *args):
        """Cancels the animation loop for a GIF."""
        self.viewer.unregister_reset_interest(self.cancel_loop)
        self.label.after_cancel(self.after_id)


class TkGifParser:
    """A parser for GIF images using the standard Tkinter PhotoImage.

    This class saves the GIF data to a temporary file and then loads it
    into a PhotoImage. It does not support animated GIFs.

    Attributes:
        tf: The temporary file object.
        tfname: The name of the temporary file.
        viewer: The viewer object.
        label: The Tkinter Label widget used to display the image.
    """

    def __init__(self, viewer, reload=0):
        """Initializes the TkGifParser.

        Args:
            viewer: The viewer object.
            reload: An optional flag indicating a reload.
        """
        self.tf = self.tfname = None
        self.viewer = viewer
        self.viewer.new_font((AS_IS, AS_IS, AS_IS, 1))
        self.tfname = tempfile.mktemp()
        self.tf = open(self.tfname, 'wb')
        self.label = Tkinter.Label(self.viewer.text, text=self.tfname,
                                   highlightthickness=0, borderwidth=0)
        self.viewer.add_subwindow(self.label)

    def feed(self, data):
        """Writes a chunk of data to the temporary file.

        Args:
            data: The chunk of data to write.
        """
        self.tf.write(data)

    def close(self):
        """Finalizes the parsing process.

        This method closes the temporary file, creates a PhotoImage from it,
        and then deletes the file.
        """
        if self.tf:
            self.tf.close()
            self.tf = None
            self.label.image = Tkinter.PhotoImage(file=self.tfname)
            self.label.config(image=self.label.image)
        if self.tfname:
            try:
                os.unlink(self.tfname)
            except os.error:
                pass


def parse_image_gif(*args, **kw):
    """Create the appropriate image handler, and replace this function with
    the handler for future references (to skip the determination step)."""

    global parse_image_gif
    if _use_pil and AsyncImage.isPILAllowed():
        parse_image_gif = PILGifParser
    else:
        parse_image_gif = TkGifParser
    return parse_image_gif(*args, **kw)
