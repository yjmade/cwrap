
typedef long long LLong;


struct Foo {
    int a;
    LLong b;
};


typedef struct _Bar {
    double b;
} Bar;


typedef enum {
    ONE,
    TWO,
    THREE,
    FOUR,
    FIVE,
} Baz;


typedef Baz Spam;


typedef struct Foo Eggs;


union AUnion {
    int a;
    double b;
    long double c;
    struct _sNested {
        char* data;
    } nested_data;
};


typedef struct _Astruct {
    Eggs *eggsPtr;
    union _uNested {
        float* data;
    } nested_data;
} Astruct;


int *foo_bar(double t, Bar *barptr);


// function which returns a pointer to an array of 10 pointers to doubles
double *(*crazy_fn(int*, char*, Baz))[10];


// pointer to function which returns pointer to array of 42 pointers to char
typedef char *(*(*crazy_fn_ptr_)(void *))[42];


