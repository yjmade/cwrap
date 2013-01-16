//nested struct

typedef struct outer 
{
  int data_outer;
  struct inner_tag
  {
    int data_inner;
  } inner;
} outer_t;
