cdef extern from "struct_different_tag_and_typedef.h":
    cdef struct tag_st:
        float foo
        int bar
    ctypedef tag_st typedef_t
