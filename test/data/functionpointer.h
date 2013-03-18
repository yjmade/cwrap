// function that that takes int and returns pointer to function that takes
// two floats and returns float
float (*returns_func_ptr(int foo))(float, float);

// function which takes pointer to char and returns pointer to function which 
// takes int and double and returns pointer to function that takes int and long
// and returns pointer to function that takes pointer to char and returns 
// pointer to double.
double *(*(*(*returns_func_ptr_nested(char*))(int, double))(int, long))(char*);

// function pointer variable declaration
double (*func_ptr_var)(void);

// function pointer variable which returns function pointer which returns int
int (*(*func_ptr_func_ptr_var)(void))(void);
