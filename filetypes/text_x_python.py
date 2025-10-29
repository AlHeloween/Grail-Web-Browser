"""<OBJECT> handler for Python applets."""

__version__ = '$Revision: 1.5 $'

import grailutil
import regex
import string
import Tkinter
import token

import AppletLoader
import sgml.HTMLParser


def embed_text_x_python(parser, attrs):
    """Handles the embedding of Python applets within a document.

    This function is called by the HTML parser when an <OBJECT> tag with a
    type of 'text/x-python' is encountered. It parses the attributes and
    creates an AppletEmbedding to handle the applet.

    Args:
        parser: The HTML parser instance.
        attrs: A list of attributes for the <OBJECT> tag.

    Returns:
        An AppletEmbedding object if the applet can be loaded, otherwise None.
    """
    extract = grailutil.extract_keyword
    width = extract('width', attrs, conv=int)
    height = extract('height', attrs, conv=int)
    menu = extract('menu', attrs, conv=str.strip)
    classid = extract('classid', attrs, conv=str.strip)
    codebase = extract('codebase', attrs, conv=str.strip)
    align = extract('align', attrs, 'baseline')
    vspace = extract('vspace', attrs, 0, conv=int)
    hspace = extract('hspace', attrs, 0, conv=int)
    apploader = AppletLoader.AppletLoader(
        parser, width=width, height=height, menu=menu,
        classid=classid, codebase=codebase,
        vspace=vspace, hspace=hspace, align=align, reload=parser.reload1)
    if apploader.feasible():
        return AppletEmbedding(apploader)
    else:
        apploader.close()
        return None


class AppletEmbedding(sgml.HTMLParser.Embedding):
    """An interface for Python applets embedded with <OBJECT> and <PARAM>
    elements.

    This class provides a simple interface for the HTML parser to interact
    with the applet loader.

    Attributes:
        __apploader: The AppletLoader instance.
    """

    def __init__(self, apploader):
        """Initializes the AppletEmbedding.

        Args:
            apploader: The AppletLoader instance.
        """
        self.__apploader = apploader

    def param(self, name, value):
        """Sets a parameter for the applet.

        Args:
            name: The name of the parameter.
            value: The value of the parameter.
        """
        self.__apploader.set_param(name, value)

    def end(self):
        """Starts the applet."""
        self.__apploader.go_for_it()


class parse_text_x_python:
    """A parser for Python source code that provides syntax highlighting.

    This class parses a Python source file, colorizes it, and displays it
    in the viewer.

    Attributes:
        __viewer: The viewer object.
        __source: The Python source code.
    """
    def __init__(self, viewer, reload=0):
        """Initializes the parser.

        Args:
            viewer: The viewer object.
            reload: An optional flag indicating a reload.
        """
        self.__viewer = viewer
        self.__source = ''
        viewer.new_font((None, 0, 0, 1))

    def feed(self, data):
        """Processes a chunk of source code.

        Args:
            data: The chunk of source code to process.
        """
        self.__source = self.__source + data
        self.__viewer.send_literal_data(data)

    IGNORED_TERMINALS = (
	token.ENDMARKER, token.NEWLINE, token.INDENT, token.DEDENT)
    __wanted_terminals = {}
    for ntype in token.tok_name.keys():
	if token.ISTERMINAL(ntype) and ntype not in IGNORED_TERMINALS:
	    __wanted_terminals[ntype] = ntype

    __ws_width = regex.compile("[%s]*" % string.whitespace).match

    def close(self):
        """Finalizes the parsing and colorizing process."""
        self.show("Colorizing Python source text - parsing...")
        import ast
        try:
            nodes = ast.parse(self.__source)
        except SyntaxError as err:
            self.__viewer.context.message(
                "Syntax error in Python source: %s" % err)
            return
        self.setup_tags()
        from types import IntType, ListType
        ISTERMINAL = token.ISTERMINAL
        wanted = self.__wanted_terminals.__contains__
        ws_width = self.__ws_width
        tag_add = self.tag_add = self.__viewer.text.tag_add
        colorize = self.colorize
        prevline, prevcol = 0, 0
        sourcetext = self.__source.split("\n")
        sourcetext.insert(0, '')
        self.show("Colorizing Python source text - coloring...")
        steps = 0
        for node in ast.walk(nodes):
            steps = steps + 1
            if not (steps % 2000): self.show()
            if hasattr(node, 'lineno'):
                lineno = node.lineno
                col_offset = node.col_offset
                if hasattr(node, 'value'):
                    nstr = str(node.value)
                    ntype = token.STRING
                elif isinstance(node, ast.Name):
                    nstr = node.id
                    ntype = token.NAME
                elif isinstance(node, ast.keyword):
                    nstr = node.arg
                    ntype = token.NAME
                else:
                    continue
                # The parser spits out the line number the token ENDS on,
                # not the line it starts on!
                if ntype == token.STRING and "\n" in nstr:
                    strlines = nstr.split("\n")
                    endpos = lineno, len(strlines[-1]), sourcetext[lineno]
                    lineno = lineno - len(strlines) + 1
                else:
                    endpos = ()
                if prevline != lineno:
                    tag_add('python:comment',
                            "%d.%d" % (prevline, prevcol), "%d.0" % lineno)
                    prevcol = 0
                    prevline = lineno
                    sourceline = sourcetext[lineno]
                prevcol = prevcol + ws_width(sourceline, prevcol)
                colorize(ntype, nstr, lineno, prevcol)
                # point prevline/prevcol to 1st char after token:
                if endpos:
                    prevline, prevcol, sourceline = endpos
                else:
                    prevcol = prevcol + len(nstr)
        # end of last token to EOF is a comment...
        start = "%d.%d" % (prevline or 1, prevcol)
        tag_add('python:comment', start, Tkinter.END)
        self.__viewer.context.message_clear()
        self.tag_add = None

    def show(self, message=None):
        """Displays a message in the status bar.

        Args:
            message: The message to display.
        """
        if message:
            self.__viewer.context.message(message)
        self.__viewer.context.browser.root.update_idletasks()

    # Each element in this table maps an identifier to a tuple of
    # the tag it should be marked with and the tag the next token
    # should be marked with (or None).
    #
    __keywords = {
	# real keywords
	'and': ('python:operator', None),
	'break': ('python:control', None),
	'class': ('python:define', 'python:class'),
	'continue': ('python:control', None),
	'def': ('python:define', 'python:def'),
	'del': ('python:statement', None),
	'elif': ('python:control', None),
	'else': ('python:control', None),
	'except': ('python:control', None),
	'finally': ('python:control', None),
	'for': ('python:control', None),
	'from': ('python:statement', None),
	'global': ('python:statement', None),
	'if': ('python:control', None),
	'import': ('python:statement', None),
	'in': ('python:operator', None),
	'is': ('python:operator', None),
	'lambda': ('python:operator', None),
	'not': ('python:operator', None),
	'or': ('python:operator', None),
	'pass': ('python:statement', None),
	'print': ('python:statement', None),
	'raise': ('python:control', None),
	'return': ('python:control', None),
	'try': ('python:control', None),
	'while': ('python:control', None),
	# others I'd like made special
	'None': ('python:special', None),
	}
    import types
    for name in dir(types):
	if len(name) > 4 and name[-4:] == "Type":
	    __keywords[name] = ('python:special', None)

    __next_tag = None
    def colorize(self, ntype, nstr, lineno, colno):
	"""Colorize a single token.

	ntype
	    Node type.  This is guaranteed to be a terminal token type
	    not listed in self.IGNORE_TERMINALS.

	nstr
	    String containing the token, uninterpreted.

	lineno
	    Line number (1-based) of the line on which the token starts.

	colno
	    Index into the source line at which the token starts. <TAB>s
	    are not counted specially.

	"""
	start = "%d.%d" % (lineno, colno)
	end = "%s + %d chars" % (start, len(nstr))
	if self.__next_tag:
	    self.tag_add(self.__next_tag, start, end)
	    self.__next_tag = None
	elif nstr in self.__keywords:
	    tag, self.__next_tag = self.__keywords[nstr]
	    self.tag_add(tag, start, end)
	elif ntype == token.STRING:
	    qw = 1			# number of leading/trailing quotation
	    if nstr[0] == nstr[1]:	# marks -- `quote width'
		qw = 3
	    start = "%d.%d" % (lineno, colno + qw)
	    end = "%s + %d chars" % (start, len(nstr) - (2 * qw))
	    self.tag_add("python:string", start, end)

    # Set foreground colors from this tag==>color table:
    __foregrounds = {
	'python:class': 'darkGreen',
	'python:comment': 'mediumBlue',
	'python:control': 'midnightBlue',
	'python:def': 'saddleBrown',
	'python:define': 'midnightBlue',
	'python:operator': 'midnightBlue',
	'python:special': 'darkGreen',
	'python:statement': 'midnightBlue',
	'python:string': 'steelblue4',
	}

    def setup_tags(self):
	"""Configure the display tags associated with Python source coloring.

	This is called only if the source is correctly parsed.  All mapping
	of logical tags to physical style is accomplished in this method.

	"""
	self.__viewer.configure_fonttag('_tt_b')
	self.__viewer.configure_fonttag('_tt_i')
	text = self.__viewer.text
	boldfont = text.tag_cget('_tt_b', '-font')
	italicfont = text.tag_cget('_tt_i', '-font')
	text.tag_config('python:string', font=italicfont)
	for tag in ('python:class', 'python:def', 'python:define'):
	    text.tag_config(tag, font=boldfont)
	for tag, color in self.__foregrounds.items():
	    text.tag_config(tag, foreground=color)
