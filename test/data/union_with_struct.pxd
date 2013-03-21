cdef extern from "union_with_struct.h":
    cdef struct __AUnion__sNested:
        char *data

    ctypedef __AUnion__sNested __AUnion__sNested_t

    cdef union AUnion:
        int a
        double b
        long double c
        __AUnion__sNested_t nested_data
