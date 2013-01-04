#define FOO 3
#define BAR 4
#define MACRO(x) (x)*2

#ifdef FOO
#define SPAM 5
#else
#define SPAM 6
#endif

int m = FOO;

// typdef of simple fundamental type
typedef long long LLong;


// struct containing typedef'd field
struct Foo {
    int a;
    LLong b;
};


// struct with tag and typedef name
typedef struct _Bar {
    double b;
} Bar;


// typedef'd anonymous enum
typedef enum {
    ONE,
    TWO,
    THREE,
    FOUR,
    FIVE,
} Baz;


// Typedef'd typedef
typedef Baz Spam;


// typedef'd struct
typedef struct Foo Eggs;


// union with nested struct
union AUnion {
    int a;
    double b;
    long double c;
    struct _sNested {
        char* data;
    } nested_data;
};


// struct with nested union
typedef struct _Astruct {
    Eggs *eggsPtr;
    union _uNested {
        float* data;
    } nested_data;
} Astruct;

/*
// double nesting
typedef struct {
    union uInner {
        float num;
    } innerU;
    struct medStruct {
        double d;
        struct innerStruct{
            int n;
        } whoa;
    } totally;
} OuterStruct;
*/

// function which returns pointer to int
int *foo_bar(double t, Bar *barptr);


// function which returns a pointer to an array of 10 pointers to doubles
double *(*crazy_fn(int*, char*, Baz))[10];


// pointer to function which returns pointer to array of 42 pointers to char
typedef char *(*(*crazy_fn_ptr_)(void *))[42];


// struct with function pointer field
struct AnotherFoo {
    int (*func)(double, int*);
};


// function that that takes int and returns pointer to function that takes
// two floats and returns float
float (*returns_func_ptr(int foo))(float, float);
/*float (*returns_func_ptr(int foo))(float, float)*/

// function which takes pointer to char and returns pointer to function which 
// takes int and double and returns pointer to function that takes int and long
// and returns pointer to function that takes pointer to char and returns 
// pointer to double.
double *(*(*(*returns_func_ptr_nested(char*))(int, double))(int, long))(char*);


// struct with function pointer field which takes int and returns pointer
// to function which takes float pointer and returns pointer to char
struct CrazyField {
    char *(*(*crazy_ptr)(int))(float*);
};


// function pointer variable declaration
double (*func_ptr_var)(void);


// function pointer variable which returns function pointer which returns int
int (*(*func_ptr_func_ptr_var)(void))(void);
