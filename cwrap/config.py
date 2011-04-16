import os


class Header(object):

    def __init__(self, path, pxd=None, pyx=None):
        self.path = os.path.abspath(path)
        self.header_name = os.path.split(self.path)[-1] 

        mod_base = self.header_name.rstrip('.h')
        
        if pxd is None:
            self.pxd = '_' + mod_base
        else:
            self.pxd = extern

        if pyx is None:
            self.pyx = mod_base
        else:
            self.pyx = pyx


class Config(object):
    
    def __init__(self, include_dirs=None, save_dir=None, headers=None):
        self.include_dirs = include_dirs or []
        self.save_dir = save_dir or os.getcwd()
        self.headers = headers or []
        
        self._header_map = {}
        for header in self.headers:
            self._header_map[header.path] = header
    
    def header(self, header_path):
        return self._header_map[header_path]

    def pxd_name(self, header_path):
        return self._header_map[header_path].pxd

    def pyx_name(self, header_path):
        return self._header_map[header_path].pyx
