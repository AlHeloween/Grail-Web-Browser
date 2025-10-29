"""audio/basic MIME type handler"""
import sounddevice as sd
import audioop

class parse_audio_basic:
    """A parser for audio/basic MIME type.

    This class handles audio/basic (u-law) data by playing it through the
    system's audio output.

    Attributes:
        stream: The sounddevice RawOutputStream for audio playback.
    """

    def __init__(self, viewer, reload=None):
        """Initializes the audio parser.

        Args:
            viewer: The viewer object.
            reload: An optional flag indicating a reload.
        """
        viewer.send_flowing_data("(Listen to the audio!)\n")
        self.stream = sd.RawOutputStream(
            samplerate=8000,
            channels=1,
            dtype='int8'  # u-law is 8-bit
        )
        self.stream.start()

    def feed(self, buf):
        """Processes a chunk of audio data.

        This method converts the u-law data to linear format and writes it
        to the audio stream.

        Args:
            buf: The chunk of audio data.
        """
        # Convert u-law to linear
        linear_data = audioop.ulaw2lin(buf, 1)
        self.stream.write(linear_data)

    def close(self):
        """Closes the audio stream."""
        self.stream.stop()
        self.stream.close()
