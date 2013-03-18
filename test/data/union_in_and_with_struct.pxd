cdef extern from "union_in_and_with_struct.h":
    cdef struct ____my_st_v_v0:
        void *cookie
        int error

    ctypedef ____my_st_v_v0 ____my_st_v_v0_t

    cdef struct ____my_st_v_v1:
        float bar2
        double baz

    ctypedef ____my_st_v_v1 ____my_st_v_v1_t

    cdef union __my_st_v:
        ____my_st_v_v0_t v0
        ____my_st_v_v1_t v1

    ctypedef __my_st_v __my_st_v_t

    cdef struct my_st:
        __my_st_v_t v
