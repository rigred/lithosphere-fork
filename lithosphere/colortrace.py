import sys, traceback, pygments
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter

lexer = PythonLexer()
formatter = TerminalFormatter()

def color_hook(type, exception, trace):
    print '\x1b[1m%s\x1b[22m' % 'Traceback (most recent call last):'
    for filename, lineno, module, sourceline in traceback.extract_tb(trace):
        print '  File \x1b[36m"%s"\x1b[39m, line \x1b[36m%i\x1b[39m, in %s' % (filename, lineno, module)
        print '    ' + highlight(sourceline, lexer, formatter).rstrip()
    print '\x1b[31m%s\x1b[39m: %s' % (type.__name__, exception)

sys.excepthook = color_hook
