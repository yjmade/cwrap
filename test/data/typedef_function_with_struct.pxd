cdef extern from "typedef_function_with_struct.h":

    ctypedef struct my_struct_t:
        int bar

    ctypedef void (*some_name)(my_struct_t *)
