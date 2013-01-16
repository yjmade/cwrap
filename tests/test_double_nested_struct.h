// double nesting
//typedef struct {
typedef struct 
//Outer_tag 
{
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

/* //gccxml

    cdef union __OuterStruct_uInner:
        float num

    cdef struct ____OuterStruct_medStruct_innerStruct:
        int n

    cdef struct __OuterStruct_medStruct:
        double d
        ____OuterStruct_medStruct_innerStruct_t whoa

    cdef struct OuterStruct:
        __OuterStruct_uInner_t innerU
        __OuterStruct_medStruct_t totally
*/

/*
//my guess
ctypedef struct OuterStruct:
   __OuterStruct_uInner_t innerU
   __OuterStruct_
*/

/* //result clang, with tagname
    cdef union __Outer_tag_uInner:
        float num

    ctypedef __Outer_tag_uInner __Outer_tag_uInner_t

    cdef struct ____Outer_tag_medStruct_innerStruct:
        int n

    ctypedef ____Outer_tag_medStruct_innerStruct ____Outer_tag_medStruct_innerStruct_t

    cdef struct __Outer_tag_medStruct:
        double d
        ____Outer_tag_medStruct_innerStruct_t whoa

    ctypedef __Outer_tag_medStruct __Outer_tag_medStruct_t

    cdef struct Outer_tag:
        __Outer_tag_uInner_t innerU
        __Outer_tag_medStruct_t totally

    ctypedef Outer_tag OuterStruct
*/
