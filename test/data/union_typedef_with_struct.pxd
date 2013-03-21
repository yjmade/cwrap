cdef extern from "union_typedef_with_struct.h":
    cdef struct __outerunion_somestruct:
        int doesntmatter

    ctypedef __outerunion_somestruct __outerunion_somestruct_t

    ctypedef union outerunion:
        int a
        __outerunion_somestruct_t somestruct
