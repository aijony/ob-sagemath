# -*- coding: utf-8; mode: sage -*-
from sage.repl.rich_output.output_catalog import OutputImagePng
from sage.repl.rich_output.backend_ipython import BackendIPythonCommandline
from sage.repl.rich_output.output_basic import OutputLatex
from sage.repl.rich_output import get_display_manager
from sage.repl.rich_output.preferences import DisplayPreferences
import sage.misc.latex
from emacs_sage_shell import ip


class LastState(object):

    def __init__(self):
        # Used for image files
        self.filename = None
        self.result = None
        self.latex = None
        self.latex_formatter = None

last_state = LastState()


class BackendEmacsBabel(BackendIPythonCommandline):

    def __init__(self, state):
        super(BackendEmacsBabel, self).__init__()
        self.__state = state

    @property
    def state(self):
        return self.__state

    def default_preferences(self):
        if self.state.latex:
            text = 'latex'
        else:
            text = None
        return DisplayPreferences(text=text)

    def latex_formatter(self, obj, **kwds):
        if self.state.latex_formatter is not None and callable(self.state.latex_formatter):
            return OutputLatex(self.state.latex_formatter(obj, **kwds))
        if 'concatenate' in kwds:
            combine_all = kwds['combine_all']
        else:
            combine_all = False
        return OutputLatex(sage.misc.latex.latex(obj, combine_all=combine_all))

    def _repr_(self):
        return "Emacs babel"

    def displayhook(self, plain_text, rich_output):
        if isinstance(rich_output, OutputImagePng):
            msg = rich_output.png.filename(ext='png')
            babel_filename = self.state.filename
            if babel_filename is not None:
                rich_output.png.save_as(babel_filename)
                msg = babel_filename
            return ({u'text/plain': msg}, {})
        else:
            return super(BackendEmacsBabel, self).displayhook(plain_text, rich_output)


gdm = get_display_manager()


def run_cell_babel(code, filename=None, latex=None, latex_formatter=None):
    last_state.filename = filename
    last_state.result = None
    last_state.latex = latex
    last_state.latex_formatter = latex_formatter

    backend_ob_sage = BackendEmacsBabel(last_state)
    with sagebackend(backend_ob_sage):
        res = ip.run_cell(code)
        if res.success:
            last_state.result = res.result
            print 1
        else:
            print 0


class WithBackEnd(object):

    def __init__(self, back_end):
        self.__back_end = back_end
        self.__prv = None

    def __enter__(self):
        self.__prv = gdm.switch_backend(self.__back_end, shell=ip)

    def __exit__(self, err_type, value, traceback):
        gdm.switch_backend(self.__prv, shell=ip)


def sagebackend(back_end):
    return WithBackEnd(back_end)


def print_last_result(module_name):
    backend_ob_sage = BackendEmacsBabel(last_state)
    with sagebackend(backend_ob_sage):
        ip.run_cell("%s.last_state.result" % module_name)
