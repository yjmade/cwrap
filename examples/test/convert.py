from cwrap.config import Config, File

if __name__ == '__main__':
    config = Config('gccxml', files=[File('test.h')])
    config.generate()
