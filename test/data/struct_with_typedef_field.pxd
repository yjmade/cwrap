cdef extern from "struct_with_typedef_field.h":
    ctypedef long long LLong

    cdef struct Foo:
        int a
        LLong b
