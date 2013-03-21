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

// function which returns pointer to int
int *foo_bar(double t, Bar *barptr);

// function which returns a pointer to an array of 10 pointers to doubles
double *(*crazy_fn(int*, char*, Baz))[10];
