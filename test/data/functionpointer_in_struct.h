// struct with function pointer field which takes int and returns pointer
// to function which takes float pointer and returns pointer to char
struct CrazyField {
    char *(*(*crazy_ptr)(int))(float*);
};
