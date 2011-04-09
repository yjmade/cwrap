from collections import defaultdict
from cStringIO import StringIO
import os
import subprocess

import pycparser

import cy_ast
import translate
import renderers


class Code(object):

    def __init__(self):
        self._io = StringIO()
        self._indent_level = 0
        self._indentor = '    '
        self._imports = defaultdict(set)
        self._imports_from = defaultdict(lambda: defaultdict(set))
        self._cimports = defaultdict(set)
        self._cimports_from = defaultdict(lambda: defaultdict(set))

    def indent(self, n=1):
        self._indent_level += n

    def dedent(self, n=1):
        self._indent_level -= n

    def write_i(self, code):
        indent = self._indentor * self._indent_level
        self._io.write('%s%s' % (indent, code))

    def write(self, code):
        self._io.write(code)

    def add_import(self, module, as_name=None):
        self._imports[module].add(as_name)

    def add_import_from(self, module, imp_name, as_name=None):
        self._imports_from[module][imp_name].add(as_name)

    def add_cimport(self, module, as_name=None):
        self._cimports[module].add(as_name)
    
    def add_cimport_from(self, module, imp_name, as_name=None):
        self._cimports_from[module][imp_name].add(as_name)

    def code(self):
        return '#imports\n' + self._io.getvalue()



class CodeGenerator(object):

    def __init__(self, header_path, include_dirs=None, module_name=None):
        self.header_path = header_path

        if include_dirs is None:
            self.include_dirs = []
        else:
            self.include_dirs = include_dirs

        if module_name is None:
            self.module_name = os.path.split(header_path)[-1].rstrip('.h')
        else:
            self.module_name = module_name

        self._extern_code = Code()
        self._pxd_code = Code()
        self._pyx_code = Code()

    def _preprocess(self):
        cmds = ['gcc']
        for inc_dir in self.include_dirs:
            cmds.append('-I' + inc_dir)
        cmds.append('-E')
        cmds.append(self.header_path)
        print cmds
        p = subprocess.Popen(cmds, stdout=subprocess.PIPE)
        c_code, _ = p.communicate()
        return c_code

    def _parse(self, c_code):
        parser = pycparser.CParser()
        ast = parser.parse(c_code)
        return ast

    def _translate(self, c_ast):
        translator = translate.ASTTranslator()
        module_ast = translator.visit(c_ast)
        return module_ast

    def generate(self):
        c_code = self._preprocess()
        c_ast = self._parse(c_code)
        module_ast = self._translate(c_ast)

        extern_code = self._extern_code
        pxd_code = self._pxd_code
        pyx_code = self._pyx_code
        codes = (extern_code, pxd_code, pyx_code)

        for item in module_ast.items:
            if isinstance(item, cy_ast.Typedef):
                renderers.render_typedef(item, *codes)
            elif isinstance(item, cy_ast.Struct):
                renderers.render_struct(item, *codes)
            elif isinstance(item, cy_ast.Enum):
                renderers.render_enum(item, *codes)

        return [code.getvalue() for code in codes]
