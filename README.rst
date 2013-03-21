==================================
libclang based frontend for cwrap 
==================================


cwrap, written by Chris Colbert, is a tool for the automatic generation of Cython_ declarations (pxd files) from C/C++ header files. 

This fork adds another frontend, using libclang_ of the llvm-project for parsing C/C++.

Requirements
------------

* the libclang library (libclang.so, libclang.dylib or libclang.dll), contained in `llvm binary distribution <http://llvm.org/releases/download.html>`_ needs to be somewhere on the binary search path.


Getting started
---------------

* checkout

* try it (in cwrap):

::

   python runtest.py tests/test.h

* have a look at the generated pxd file

::

   less tests/result_clang/_test.pxd

* Additional testing (this command needs Python 2.7):

::

   python -m unittest discover -s test


Current status
--------------

For C headers the libclang frontend produces useful results. 

Rudimentary support for parsing C++ headers is provided. Known problems exist with supporting following C++ features:

* class template (libclang misses support)
* nested class definitions
* default arguments
* namespaces

Ideas for improvements
----------------------

* tests, tests, tests.

* provide a way to configure which declarations get exposed (especially for nested includes),  e.g., no definitions from system includes, give list of header files, ...

* libclang enables parsing of comments, supporting doxygen syntax. automatically generate documentation comments. does cython support this for cdef extern?

Contributors
------------

Chris Colbert (original cwrap), Gregor Thalhammer and Volker Mische (libclang frontend)

.. _Cython: http://www.cython.org
.. _libclang: http://clang.llvm.org/doxygen/group__CINDEX.html
