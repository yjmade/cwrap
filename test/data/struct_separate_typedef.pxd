cdef extern from "struct_separate_typedef.h":
    cdef struct tag_st:
        float foo
        int bar
    ctypedef tag_st typedef_t
