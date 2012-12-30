#define CONST 2


//anonymous enum
enum
  {E_ONE,
   E_TWO
  };
/* cdef enum:
   ...
*/
/* ENUM_DECL '' */
//OK


//named enum
enum E0
  {
    E0_ONE,
    E0_TWO
  };
//cdef enum E0: ...
/* ENUM_DECL 'E0_tn' */
//OK


typedef long long LLong;

//typename only
typedef enum
{
  E1_ONE,
  E1_TWO = 2
} E1_type;
/* ctypedef enum E1_type: ... */
/* ENUM_DECL ''
   TYPEDEF_DECL 'E1_type', unnamed type declaration
*/
//FAIL: cdef enum: ... + ctypedef  E1_type
//FIX?: combine ctypedef with previous enum, remove enum (if empty first argument ctypedef)


// both tagname and typename
typedef enum E2_tag {
  E2_ONE,
  E2_TWO = CONST
} E2_type;
/* cdef enum E2_tag:
   ...
   ctypedef E2_tag E2_type

   or

   ctypedef enum E2_type: ...
*/
/* ENUM_DECL 'E2_tag'
   TYPEDEF_DECL 'E2_type', type declaration 'E2_tag'
*/
//OK


// same name for tag and typedef
typedef enum E3 {
  E3_ONE,
  E3_TWO
} E3;
/*cdef enum E3*/
/* ENUM_DECL 'E3'
   TYPEDEF_DECL 'E3', type declaration 'E3'
*/
//FAIL: cdef enum E3: + ctypedef E3 E3
//FIX: remove ctypedef if both arguments are the same


