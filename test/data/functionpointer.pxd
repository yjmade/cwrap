cdef extern from "functionpointer.h":
    float (*returns_func_ptr(int foo))(float, float)

    double *(*(*(*returns_func_ptr_nested(char *))(int, double))(int, long))(char *)


    double (*func_ptr_var)()

    int (*(*func_ptr_func_ptr_var)())()
