# Grail: An Extensible Internet Browser in Python

Grail is a web browser written entirely in Python. Originally developed in the mid-1990s, this version has been updated to be compatible with Python 3.11. Grail is notable for its extensibility, allowing developers to easily add new functionality and protocols.

## Features

*   **Extensible:** Grail's architecture makes it easy to add new protocol handlers, MIME type parsers, and HTML tag handlers.
*   **Python-based:** Written entirely in Python, Grail is easy to understand and modify.
*   **Cross-platform:** Grail runs on most Unix systems, Windows, and macOS.

## Requirements

*   Python 3.11 or newer
*   Tcl/Tk 8.0 or newer
*   `sounddevice` library

## Installation

1.  **Install Python and Tcl/Tk:** Ensure that you have a compatible version of Python and Tcl/Tk installed on your system.
2.  **Install Dependencies:** Install the `sounddevice` library using pip:

    ```bash
    pip install -r requirements.txt
    ```

3.  **Run Grail:** Execute the `grail.py` script to start the browser:

    ```bash
    python grail.py [options] [url]
    ```

## Usage

### Command-line Options

*   `-i`, `--noimages`: Inhibit loading of images.
*   `-g <geom>`, `--geometry <geom>`: Set the initial window geometry (e.g., `800x600+100+100`).
*   `-d <display>`, `--display <display>`: Override the `$DISPLAY` environment variable.
*   `-q`: Ignore the user's `grailrc.py` file.

### Examples

*   Start Grail and load the default home page:

    ```bash
    python grail.py
    ```

*   Load a specific URL:

    ```bash
    python grail.py http://www.python.org/
    ```

*   Start Grail without loading images and with a specific window size:

    ```bash
    python grail.py -i -g 1024x768
    ```

## Contributing

Contributions to Grail are welcome! If you'd like to contribute, please fork the repository and submit a pull request.

## License

Grail is licensed under the CNRI License Agreement. See the `LICENSE` file for more information.
