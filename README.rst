==================================
libclang based frontend for cwrap 
==================================


cwrap, written by Chris Colbert, is a tool for the automatic generation of Cython_ declarations (pxd files) from C header files. 

This fork adds another frontend, using libclang_ of the llvm-project for parsing C/C++.

Getting started
---------------

* checkout (note development happens in branch development and feature/XXX)

* copy binary of libclang library (libclang.so, libclang.dylib or libclang.dll), contained in `llvm binary distribution <http://llvm.org/releases/download.html>`_ into .../cwrap/frontends/clang/clang

* try it (in cwrap):

::

   python runtest.py tests/test.h

* hav a look at the generated pxd file

::
   less tests/result_clang/_test.pxd

.. _Cython: http://www.cython.org
.. _libclang: http://clang.llvm.org/doxygen/group__CINDEX.html
