cdef extern from "function.h":
    cdef struct _Bar:
        double b
    ctypedef _Bar Bar

    ctypedef enum Baz:
        ONE
        TWO
        THREE
        FOUR
        FIVE

    int *foo_bar(double t, Bar *barptr)

    double *(*crazy_fn(int *, char *, Baz))[10]
