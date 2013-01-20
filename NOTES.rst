PERSONAL NOTES
==============

for development of libclang frontend


most relevant files
-------------------

cwrap/cwrap/frontends/clang/clang_parser.py:


TESTS
-----

convert C header file to .pxd:

> python convert.py tests/test.h | less ; less tests/result_clang/_test.pxd 

show C AST of C header file:

> python libclang_show_ast.py tests/test.h | less



PROBLEMS
--------

nested structs without typename/tagname: try all combinations

double nested structure

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

ok if tag name for OuterStruct is added !?

in ast_transforms.py:flatten_nested_containers


* void return type: omit it

TODO

struct Node {
    int data;
    struct Node *nextptr;
};

should be equivalent to:

typedef struct Node Node;
struct Node {
    int data;
    Node *nextptr;
};

* function declaration with no arguments

int foo()

gives FUNCTION_DECL, with Kind FUNCTIONNOPROTO, get_arguments violates
assert.
   * patch cindex.py ?
   * should be int foo(void)
   * difference C/C++ ? 
   
   empty parameter list
   C:, function takes unknown number of
   parameters, 
   C++: takes no parameters/


TODOS
=====

* parse macro definition, add as enum.  How to recognized constants
  and macro functions?

* handle includes. How to avoid wrapping system includes?

* parse cppclass definition: templates, ...

* parse doxygen documentation: need to update Index.h


TEST CASES
==========

some other test cases

cython-codegen

pyzmq

own projects
------------

mv

pyrawte

eos





OLD STUFF
=========


Funktion:
clang_parser.py:
   visit_XXX_DECL() -> generates c_ast object
(fix_XXX)

ast_transforms.py:
    apply_c_ast_transformations
    visit_XXX -> append cw_ast object to pxd_nodes

TODO: visit_Typedef: extend for enum/struct/union:





TODO: parsed c_ast nodes stored in dict (no order), then sorted by
file/linenumber (ast_transforms) 
CHANGED: store nodes in parse order,
no sorting) -> PROBLEM: some nodes (enum typedefs) duplicated (in
type_to_c_ast_type type parse() - which stores nodes - is called again
for already parsed type
-> check in type_to_c_ast_typewhether declaration already exist, do
special handling for enums (in type_to_c_ast or visit_Typedef?) , i.e., if unnamed enum, remove enum
declaration from nodes list, or no typedef if typename equals tagname 
TODO: revert visit_Typedef
TODO: revert use of sorted nodes list



-> Typedef node: add field 'extended type' (for structs/enums)



FUNCTION DECLARATIONS

Example:
// function that that takes int and returns pointer to function that takes
// two floats and returns float
float (*returns_func_ptr(int foo))(float, float);

FUNCTION_DECL, children are float, float and int (should only be int !?)

cursor.type.argument_types() gives correct arguments, but only types

Solution:
expose 
CINDEX_LINKAGE int clang_Cursor_getNumArguments(CXCursor C);
in cindex.py, similar to argument_types()
-> already done in latest version of cindex.py, problem solved


MACROS

#define FOO 3
#define BAR 4

should end up as

enum:
    FOO
    BAR

what about

#ifdef FOO
#define BAR 3
#else
#define BAR 4
#endif

-> clang parser: #if 's are processed, #defines exposed



Notes:

1) Testläufe

in cwrap

python convert.py test_typedef.h
less result_clang/_test_typedef.pxd

python convert.py test_enums.h | less ; less result_clang/_test_enums.pxd 

Vergleich:

in pyclang

python libclang_show_ast.py ../cwrap/test_typedef.h

2) Documentation:

libclang
direkt im Quelltext python bindings, cindex.py
auch Index.h (irgendwo in Devel/clang-git/.../clang-c/)


Probleme:
--------

1)

typedef enum {ONE, TWO} twonumbers;

a) libclang liefert ENUM (unnötig?) und TYPEDEF, letzteres verschwindet
b) cwrap mit gccxml-frontend liefert: c_ast.Enumeration mit name
gesetzt



note aus cython docs: 

file:///Users/gregor/Devel/cython/docs/build/html/src/userguide/external_C_code.html?highlight=enum#styles-of-struct-union-and-enum-declaration

typedef enum {} twonumbers;  ->  ctypedef enum twonumbers: ...

enum twonumber {...}; -> cdef enum twonumber: ...

typedef enum tn {} twonumber; 
-> cdef enum tn: ...; ctypedef tn twonumber

typedef enum twonumber {} twonumber; -> cdef enum twonumber: ...


same for struct and union

TODO: testcase enums:
--> test_enums.h !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
alle Varianten aufgenommen, dort alle Ideen





IDEA:
make enums public: (cython mailing list, Niklas R, 19.2.2012)

def extern from xxx:
   enum:
       cfoo "FOO"

foo = cfoo


or (Chris Barker):

We have a bunch of code we're wrapping that used a bunch of enums
(mostly anonymous, though I don't think that makes a difference here).

so part of a heady may look like:

enum {  OILSTAT_NOTRELEASED = 0,
       OILSTAT_INWATER = 2,
       OILSTAT_ONLAND = 3,
       OILSTAT_OFFMAPS = 7,
       OILSTAT_EVAPORATED = 10};

enum {  TEST1,
       TEST2,
       TEST3
};


I want to be able to see these both from Cython as from Python. So
I"ve written a pxi like:

"""
a pxi file interface file for the enum sample
"""

cdef extern from "sample_enum.h":
   ctypedef enum:
       OILSTAT_NOTRELEASED
       OILSTAT_INWATER
       OILSTAT_ONLAND
       OILSTAT_OFFMAPS
       OILSTAT_EVAPORATED

   ctypedef enum:
       TEST1
       TEST2
       TEST3

#cdef public enum type_defs:
cdef public enum:
   status_not_released = OILSTAT_NOTRELEASED
   status_in_water = OILSTAT_INWATER
   status_on_land = OILSTAT_ONLAND
   status_off_maps = OILSTAT_OFFMAPS
   status_evaporated = OILSTAT_EVAPORATED
   test1 = TEST1
   test2 = TEST2
   test3 = TEST3


and now a simpel pyx that does nothing but include the pxi:

"""
a simple Cython file to test use of enums
"""

# nothing here! only the use of the pxi file.

include "sample_enum.pxi"




IDEA: macros

#define C_BAR 1

cdef extern from 'foo.h':
   enum: 
       C_BAR

or:
  enum:
      C_BAR_c "C_BAR"
C_BAR = C_BAR_c


???
cpdef int C_BAR




TESTCASES:

need testcases, better organization into file orders, with expected
output


c++: possible testcases:

pyzmq (cython based wrapper for zmq)

libclang, Index.h

