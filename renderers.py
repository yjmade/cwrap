import cy_ast


#------------------------------------------------------------------------------
# Struct
#------------------------------------------------------------------------------

def _render_struct_property_get(field, code):
    code.write_i('def __get__(self):\n')
    code.indent()
    name = field.identifier
    c_type = field.typ.c_type()
    code.write_i('cdef %s %s = self.%s\n' % (c_type, name, name))
    code.write_i('return %s\n\n' % field.typ.c_var_to_object(name))
    code.dedent()
    

def _render_struct_property_set(field, code):
    name = field.identifier
    code.write_i('def __set__(self, %s):\n' % name)
    code.indent()
    c_type = field.typ.c_type()
    convert = field.typ.object_var_to_c(name)
    code.write_i('cdef %s cval = %s\n' % (c_type, convert))
    code.write_i('self.%s = cval\n\n' % name)
    code.dedent()


def _render_struct_property(field, code):
    name = field.identifier
    code.write_i('property %s:\n\n' % name)
    code.indent()
    if 'r' in field.mode:
        _render_struct_property_get(field, code)
    if 'w' in field.mode:
        _render_struct_property_set(field, code)
    code.dedent()


def _render_struct_impl(struct, code):
    name = struct.identifier
    code.write_i('cdef class %s:\n\n' % name)
    code.indent()
    code.write_i('def __cinit__(self):\n')
    code.indent()
    code.write_i('self.thisptr = <%s*>PyMem_Malloc(sizeof(%s))\n\n' % (name, name))
    code.dedent()
    code.write_i('def __dealloc__(self):\n')
    code.indent()
    code.write_i('PyMem_Free(self.thisptr)\n\n')
    code.dedent()
    for field in struct.fields:
        _render_struct_property(field, code)
    code.dedent()


def _render_struct_def(struct, code):
    name = struct.identifier
    code.write_i('cdef class %s:\n\n' % name)
    code.indent()
    code.write_i('cdef %s* thisptr\n\n' % name)
    code.dedent()


def _render_extern_struct_field(field, code):
    name = field.identifier
    c_type = field.typ.c_type()
    code.write_i('%s %s\n' % (c_type, name))


def _extern_struct_field_loop(struct, code):
    code.indent()
    for field in struct.fields:
        _render_extern_struct_field(field, code)
    code.dedent()


def _render_extern_struct(struct, code):
    st_name = struct.identifier
    if isinstance(struct.parent, cy_ast.Typedef):
        td_name = struct.parent.identifier
        if td_name == st_name:
            code.write_i('cdef struct %s:\n' % st_name)
            _extern_struct_field_loop(struct, code)
        elif st_name is None:
            code.write_i('ctypdef struct %s:\n' % td_name)
            _extern_struct_field_loop(struct, code)
        else:
            code.write_i('cdef struct %s:\n' % st_name)
            _extern_struct_field_loop(struct, code)
            code.write_i('ctypedef %s %s\n' % (st_name, td_name))
    else:
        code.write_i('cdef struct %s:\n' % st_name)
        _extern_struct_field_loop(struct, code)
    code.write('\n')


def render_struct(struct, extern_code, pxd_code, pyx_code):
    _render_extern_struct(struct, extern_code)
    _render_struct_def(struct, pxd_code)
    _render_struct_impl(struct, pyx_code)


#------------------------------------------------------------------------------
# Union
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
# Enum
#------------------------------------------------------------------------------

def _render_enum_value(enum_value, last_value, code):
    name = enum_value.identifier
    value = enum_value.value
    if value is None:
        value = last_value + 1
    code.write_i('%s = %s\n' % (name, value))
    return value


def _render_enum_impl(enum, code):
    last_value = -1
    for value in enum.values:
        last_value = _render_enum_value(value, last_value, code)
    code.write_i('\n')


def _render_extern_enum_value(enum_value, code):
    name = enum_value.identifier
    code.write_i('%s\n' % name)


def _extern_enum_value_loop(enum, code):
    code.indent()
    for value in enum.values:
        _render_extern_enum_value(value, code)
    code.dedent()


def _render_extern_enum(enum, code):
    en_name = enum.identifier
    if isinstance(enum.parent, cy_ast.Typedef):
        td_name = enum.parent.identifier
        if td_name == en_name:
            code.write_i('cdef enum %s:\n' % en_name)
            _extern_enum_value_loop(enum, code)
        elif en_name is None:
            code.write_i('ctypdef enum %s:\n' % td_name)
            _extern_enum_value_loop(enum, code)
        else:
            code.write_i('cdef enum %s:\n' % en_name)
            _extern_enum_value_loop(enum, code)
            code.write_i('ctypedef %s %s\n' % (en_name, td_name))
    else:
        code.write_i('cdef enum %s:\n' % en_name)
        _extern_enum_value_loop(enum, code)
    code.write('\n')


def render_enum(enum, extern_code, pxd_code, pyx_code):
    # Enum's don't need to be written to pxd files
    _render_extern_enum(enum, extern_code)
    _render_enum_impl(enum, pyx_code)


#------------------------------------------------------------------------------
# Typedef
#------------------------------------------------------------------------------

def render_typedef(typedef, extern_code, pxd_code, pyx_code):
    if isinstance(typedef.typ, cy_ast.Struct):
        render_struct(typedef.typ, extern_code, pxd_code, pyx_code)
    elif isinstance(typedef.typ, cy_ast.Enum):
        render_enum(typedef.typ, extern_code, pxd_code, pyx_code)
    elif isinstance(typedef.typ, cy_ast.Typedef):
        render_typedef(typedef.typ, extern_code, pxd_code, pyx_code)


#------------------------------------------------------------------------------
# Function
#------------------------------------------------------------------------------

