import os

from cwrap.config import Config, Header
from cwrap.codegen import generate


if __name__ == '__main__':
    config = Config(headers=[Header('test.h')])
    generate(config)
