import tempfile
import os
import string
from grailutil import getenv, which
from Tkinter import *
from formatter import AS_IS

_FILTERCMD = 'djpeg'
_FILTERARG = '-gif'
_FILTERPATH = which(_FILTERCMD, getenv('PATH').split(':'))

if hasattr(os, 'popen') and _FILTERPATH:
    _FILTER = _FILTERPATH + ' ' + _FILTERARG
 
    class parse_image_jpeg:
    
        """A parser for JPEG images.

        This class uses an external filter program (djpeg) to convert the JPEG
        data to GIF format, which is then displayed.

        Attributes:
            broken: A flag indicating whether the image is broken.
            tf: The temporary file object.
            tfname: The name of the temporary file.
            viewer: The viewer object.
            label: The Tkinter Label widget used to display the image.
        """
    
        def __init__(self, viewer, reload=0):
            """Initializes the JPEG parser.

            Args:
                viewer: The viewer object.
                reload: An optional flag indicating a reload.
            """
            self.broken = None
            self.tf = self.tfname = None
            self.viewer = viewer
            self.viewer.new_font((AS_IS, AS_IS, AS_IS, 1))
            self.tfname = tempfile.mktemp()
            self.tf = os.popen(_FILTER + '>' + self.tfname, 'wb')
            self.label = Label(self.viewer.text, text=self.tfname,
                               highlightthickness=0, borderwidth=0)
            self.viewer.add_subwindow(self.label)
    
        def feed(self, data):
            """Writes a chunk of data to the filter program.

            Args:
                data: The chunk of JPEG data to write.
            """
            try:
                self.tf.write(data)
            except IOError as e:
                self.tf.close()
                self.tf = None
                self.broken = 1
                raise e
    
        def close(self):
            """Finalizes the parsing process.

            This method closes the pipe to the filter program, creates a
            PhotoImage from the resulting GIF file, and then deletes the file.
            """
            if self.tf:
                self.tf.close()
                self.tf = None
                self.label.image = PhotoImage(file=self.tfname)
                self.label.config(image=self.label.image)
            if self.tfname:
                try:
                    os.unlink(self.tfname)
                except os.error:
                    pass
            if self.broken:
                # TBD: horrid kludge... don't hate me! ;-)
                self.label.image = PhotoImage(file='icons/sadsmiley.gif')
                self.label.config(image=self.label.image)
                self.viewer.text.insert(END, '\nBroken Image!')
