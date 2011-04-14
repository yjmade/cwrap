from collections import defaultdict
from cStringIO import StringIO
import os
import re
import subprocess

import pycparser

import cy_ast
import translate
import renderers

    
class CodeGenerator(object):

    def __init__(self, config):
        self.config = config
        self._translator = translate.ASTTranslator()
        self._extern_renderer = renderers.ExternRenderer()

    def _preprocess(self, header):
        cmds = ['gcc']
        for inc_dir in self.config.include_dirs:
            cmds.append('-I' + inc_dir)
        cmds.append('-E')
        cmds.append(header.path)
        p = subprocess.Popen(cmds, stdout=subprocess.PIPE)
        c_code, _ = p.communicate()
        
        # we need to remove any gcc __attribute__ declarations 
        # from the code as this will cause PyCParser to fail.
        c_code = re.sub('__attribute__\(\(.*?\)\)', '', c_code)
        
        return c_code

    def _parse(self, c_code):
        parser = pycparser.CParser()
        ast = parser.parse(c_code)
        return ast

    def _translate(self, c_ast):
        module_ast = self._translator.translate(c_ast)
        return module_ast

    def _render_extern(self, module_ast, header):
        return self._extern_renderer.render(module_ast, header)

    def generate(self):
        save_dir = self.config.save_dir
        for header in self.config.headers:
            c_code = self._preprocess(header)
            c_ast = self._parse(c_code)
            module_ast = self._translate(c_ast)
            
            extern_code = self._render_extern(module_ast, header)
            extern_name = '_' + header.mod_name + '.pxd'
            extern_save_pth = os.path.join(save_dir, extern_name)

            with open(extern_save_pth, 'w') as f:
                f.write(extern_code)

