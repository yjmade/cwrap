import os

from cwrap.config import Config, Header
from cwrap.codegen import generate

BASE_PATH = '/Developer/opt/intel/ipp/include'

headers = []
for item in os.listdir(BASE_PATH):
    if item.endswith('.h'):
        if item != 'mkl_gmp.h':
            headers.append(Header(os.path.join(BASE_PATH, item)))

if __name__ == '__main__':
    config = Config(include_dirs=[BASE_PATH],
                    save_dir='.',
                    headers=headers)
    generate(config)
