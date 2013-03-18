cdef extern from "union_in_struct.h":
    cdef union __my_st_v:
        float bar
    ctypedef __my_st_v __my_st_v_t

    cdef struct my_st:
        int foo
        __my_st_v_t v
