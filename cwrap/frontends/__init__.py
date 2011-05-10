import os
import pkgutil


# find all the names of the frontend packages
_frontend_packages = set()
_pkg_path = os.path.split(__file__)[0]
for importer, name, is_pkg in pkgutil.iter_modules([_pkg_path]):
    _frontend_packages.add(name)


def get_frontend(name):
    err_msg = 'Frontend `%s` not found.' % name
    
    if name not in _frontend_packages:
        raise ImportError(err_msg)

    try:
        frontend = __import__('cwrap.frontends.' + name, fromlist=['cwrap'])
    except ImportError, e:
        raise ImportError(err_msg)
    
    return frontend


