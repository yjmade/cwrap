cdef extern from "struct_empty_struct.h":
    cdef struct tag_st:
        pass
    ctypedef tag_st typedef_t
