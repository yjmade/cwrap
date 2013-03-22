cdef extern from "const_argument.h":
    int foo(const char *bar)
    cdef struct my_st:
        pass
    ctypedef my_st my_t
    int baz(const my_t **foo)
    int bar(const my_t *const *something)
    int another(my_t *const *one)
    int yet(my_t *const *const another)
