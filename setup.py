from distutils.core import setup


setup(name='CWrap',
      version='0.0',
      description='Automatical generate Cython wrappers from C header files',
      packages=['cwrap', 'cwrap.backend', 'cwrap.frontends', 
                'cwrap.frontends.gccxml',
                'cwrap.frontends.clang',
                ]
      )
