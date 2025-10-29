"""text/plain variant that implements the format=flowed variant.

This variant is documented in the internet draft draft-gellens-format-01.txt,
dated 30 October 1998 (work in progress).

Future versions of this draft may change substantially, or it may be dropped
completely.

The 'quoted' feature is not implemented at this time.
"""

__version__ = '$Revision: 2.4 $'


import formatter
import string

from formatter import AS_IS


class FlowingTextParser:
    """A parser for text/plain with format=flowed.

    This class parses text that follows the format=flowed specification,
    handling flowing and fixed paragraphs.

    Attributes:
        buffer: A buffer for incomplete lines.
        flowing: A flag indicating whether the text is currently flowing.
        signature: A flag indicating whether a signature block has been
            encountered.
        viewer: The viewer object to which the parsed text is sent.
        formatter: The formatter object used to format the text.
    """
    buffer = ''
    flowing = 0
    signature = 0

    def __init__(self, viewer, reload=0):
        """Initializes the FlowingTextParser.

        Args:
            viewer: The viewer object.
            reload: An optional flag indicating a reload.
        """
        self.viewer = viewer
        self.formatter = formatter.AbstractFormatter(viewer)
        self.set_flow(1)

    def feed(self, data):
        """Processes a chunk of text.

        This method analyzes the text line by line to determine whether it
        is part of a flowing or fixed paragraph, and sends it to the
        formatter accordingly.

        Args:
            data: The chunk of text to process.
        """
        data = self.buffer + data
        self.buffer = ''
        if self.signature:
            self.send_data(data)
        else:
            lines = data.splitlines()
            if lines:
                self.buffer = lines[-1]
                for line in lines[:-1]:
                    if line == '-- ':
                        self.signature = 1
                        self.set_flow(0)
                    if self.signature:
                        self.send_data(line + '\n')
                        continue
                    if len(string.rstrip(line)) == (len(line) - 1) \
                       and line[-1] == ' ':
                        self.set_flow(1)
                        self.send_data(line + '\n')
                    else:
                        self.set_flow(0)
                        self.send_data(line + '\n')

    def close(self):
        """Finalizes the parsing process.

        This method sends any remaining data in the buffer to the formatter.
        """
        self.send_data(self.buffer)

    def send_data(self, data):
        """Sends data to the formatter.

        Args:
            data: The data to send.
        """
        if self.flowing:
            self.formatter.add_flowing_data(data)
        else:
            self.formatter.add_literal_data(data)

    def set_flow(self, flow):
        """Sets the flowing mode.

        Args:
            flow: A boolean indicating whether to enable or disable flowing
                mode.
        """
        flow = not not flow
        if self.flowing != flow:
            if self.flowing:
                self.formatter.add_line_break()
            self.flowing = flow
            self.viewer.new_font((AS_IS, AS_IS, AS_IS, not flow))
