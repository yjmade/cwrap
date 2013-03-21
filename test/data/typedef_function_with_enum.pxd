cdef extern from "typedef_function_with_enum.h":
    ctypedef enum my_enum_t:
        AN_ENUM_FIELD

    ctypedef void (*some_name)(my_enum_t)
