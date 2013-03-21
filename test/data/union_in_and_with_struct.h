struct my_st {
    union {
        struct {
            void *cookie;
            int error;
        } v0;
        struct {
            float bar2;
            double baz;
        } v1;
    } v;
};
