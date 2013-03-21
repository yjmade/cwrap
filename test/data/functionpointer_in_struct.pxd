cdef extern from "functionpointer_in_struct.h":
    cdef struct CrazyField:
            char *(*(*crazy_ptr)(int))(float *)
