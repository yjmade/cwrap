
# Sufficiently protect the version from being 
# modified at run time
class version(object):

    __major__ = '0'
    __minor__ = '0'
    __bugfix__ = '0'

    def __call__(self):
        return '.'.join([self.__major__, self.__minor__, self.__bugfix__])

version = version()
