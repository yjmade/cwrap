import os

from . import frontends
from .backend import renderer


class ASTContainer(object):

    def __init__(self, module, filename):
        self.module = module
        self.filename = filename


class File(object):

    def __init__(self, path, **metadata):
        self.path = os.path.abspath(path)
        self.metadata = metadata


class Config(object):
    
    def __init__(self, frontend, files, save_dir=None, **metadata):
        self.frontend = frontend
        self.files = files
        self.save_dir = save_dir or os.getcwd()
        self.metadata = metadata

    def generate(self):
        frontend = frontends.get_frontend(self.frontend)
        cw_asts = frontend.generate_asts(self)
        ast_renderer = renderer.ASTRenderer()
        for ast_container in cw_asts:
            filename = ast_container.filename
            save_path = os.path.join(self.save_dir, filename)
            print('Rendering %s' % save_path) 
            mod_node = ast_container.module
            code = ast_renderer.render(mod_node)
            try:
                with open(save_path, 'wb') as f:
                    f.write(code)
            except IOError:
                msg = 'Could not gain write access to %s' % save_path
                raise IOError(msg)


