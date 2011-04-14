import os


class Header(object):

    def __init__(self, path, mod_name=None):
        self.path = path
        self.header_name = os.path.split(path)[-1]

        if mod_name is None:
            self.mod_name = self.header_name.rstrip('.h')
        else:
            self.mod_name = mod_name


class Config(object):
    
    def __init__(self, include_dirs=None, save_dir=None, headers=None):
        self.include_dirs = include_dirs or []
        self.save_dir = save_dir or os.getcwd()
        self.headers = headers or []


