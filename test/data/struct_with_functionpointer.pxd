cdef extern from "struct_with_functionpointer.h":
    cdef struct my_st:
        int (*my_fp)(float, int)
