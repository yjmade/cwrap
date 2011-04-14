import os

from cwrap.config import Config, Header
from cwrap.codegen import CodeGenerator


def run():
    config = Config(include_dirs=[os.path.join(os.getcwd(), 'fake_libc_include'),
                                  os.getcwd()],
                    headers=[Header(path=os.path.join(os.getcwd(), 'nfft3.h'))])

    generator = CodeGenerator(config)

    generator.generate()

if __name__ == '__main__':
    run()
